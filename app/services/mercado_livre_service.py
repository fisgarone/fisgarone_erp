# app/services/mercado_livre_service.py - VERSÃO DE ENGENHARIA VALIDADA

import asyncio
import aiohttp
import os
from datetime import datetime, timedelta
import pytz
from dateutil import parser
from sqlalchemy.exc import SQLAlchemyError
from app import create_app
from app.extensions import db
from app.models.company import Company, IntegrationConfig
from app.models.ml_models import VendaML
import logging

# Configuração de logging padronizada e corrigida
logging.basicConfig(level=logging.INFO, format='%(asctime )s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MercadoLivreService:
    """
    Serviço de integração com a API do Mercado Livre, reconstruído para garantir
    resiliência, conformidade com a API e eficiência.
    """

    def __init__(self, app_context=None):
        self.api_url = os.environ.get("API_URL", "https://api.mercadolibre.com")
        self.app = app_context if app_context else create_app()

    # --- CAMADA DE ACESSO A DADOS (COM CONTEXTO) ---
    def _get_company_credentials(self, company_id):
        with self.app.app_context():
            config = IntegrationConfig.query.filter_by(company_id=company_id, ml_ativo=True).first()
            if not config:
                logger.error(f"Configuração ML ativa não encontrada para empresa {company_id}")
                return None
            return {
                'client_id': config.ml_app_id, 'client_secret': config.ml_client_secret,
                'access_token': config.ml_access_token, 'refresh_token': config.ml_refresh_token,
                'seller_id': config.ml_seller_id, 'company_id': company_id
            }

    def _update_company_tokens(self, company_id, access_token, refresh_token):
        with self.app.app_context():
            try:
                config = IntegrationConfig.query.filter_by(company_id=company_id).first()
                if config:
                    config.ml_access_token = access_token
                    if refresh_token: config.ml_refresh_token = refresh_token
                    config.ml_token_expires = datetime.utcnow() + timedelta(hours=4)
                    config.data_atualizacao = datetime.utcnow()
                    db.session.commit()
                    logger.info(f"Tokens atualizados no DB para empresa {company_id}")
            except SQLAlchemyError as e:
                db.session.rollback()
                logger.error(f"Erro de DB ao atualizar tokens para empresa {company_id}: {e}")

    # --- CAMADA DE REQUISIÇÃO ROBUSTA (BASEADO NO SCRIPT VALIDADO) ---
    async def _make_api_request(self, session, url, method='GET', headers=None, data=None, params=None, max_retries=3):
        for attempt in range(max_retries):
            try:
                async with session.request(method, url, headers=headers, data=data, params=params) as response:
                    if 200 <= response.status < 300: return await response.json()
                    if response.status == 401: return "token_invalido"
                    if response.status == 429:
                        logger.warning(f"Rate limit (429) atingido. Aguardando {(attempt + 1) * 2}s.")
                        await asyncio.sleep((attempt + 1) * 2)
                        continue
                    logger.error(f"Erro de API {response.status} em {url}: {await response.text()}")
                    return None
            except Exception as e:
                logger.error(f"Exceção na requisição (tentativa {attempt + 1}): {e}")
                if attempt < max_retries - 1: await asyncio.sleep(1)
        return None

    async def _refresh_token(self, credentials, session):
        url = f"{self.api_url}/oauth/token"
        payload = {'grant_type': 'refresh_token', 'client_id': credentials['client_id'],
                   'client_secret': credentials['client_secret'], 'refresh_token': credentials['refresh_token']}
        # Header explícito para garantir conformidade com a API
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        result = await self._make_api_request(session, url, 'POST', headers=headers, data=payload)

        if result and isinstance(result, dict):
            logger.info(f"Token renovado com sucesso para empresa {credentials['company_id']}")
            return result.get('access_token'), result.get('refresh_token')

        logger.error(f"Falha ao renovar token para empresa {credentials['company_id']}. Resposta: {result}")
        return None, None

    # --- CAMADA DE PROCESSAMENTO DE DADOS ---
    async def _process_single_order(self, order_data, credentials):
        order_id = order_data.get("id")
        with self.app.app_context():
            try:
                for item in order_data.get("order_items", []):
                    venda = VendaML.query.get(order_id) or VendaML(id_pedido=order_id)
                    venda.company_id = credentials['company_id']
                    venda.situacao = order_data.get('status')
                    venda.data_venda = parser.parse(order_data.get("date_created"))
                    venda.quantidade = item.get('quantity')
                    venda.preco_unitario = item.get('unit_price')
                    venda.mlb = item.get('item', {}).get('id')
                    venda.sku = item.get('item', {}).get('seller_sku')
                    venda.titulo = item.get('item', {}).get('title')
                    venda.taxa_ml = item.get('sale_fee')
                    db.session.add(venda)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                logger.error(f"Erro ao processar e salvar pedido {order_id}: {e}")

    async def _process_order_batch(self, orders, credentials):
        tasks = [self._process_single_order(order, credentials) for order in orders]
        await asyncio.gather(*tasks)

    async def _fetch_all_orders_for_company(self, credentials, session, days_back, hours_back):
        headers = {"Authorization": f"Bearer {credentials['access_token']}"}
        now_br = datetime.now(pytz.timezone('America/Sao_Paulo'))
        start_date = now_br - (timedelta(days=days_back) if days_back else timedelta(hours=hours_back or 1))
        start_date_str = start_date.isoformat()
        logger.info(f"📦 Buscando pedidos de {start_date_str} para empresa {credentials['company_id']}")
        offset, limit, total_pedidos_processados = 0, 50, 0

        while True:
            params = {'seller_id': credentials['seller_id'], 'sort': 'date_desc',
                      'order.date_created.from': start_date_str, 'offset': offset, 'limit': limit}
            data = await self._make_api_request(session, f"{self.api_url}/orders/search", 'GET', headers=headers,
                                                params=params)

            if data == "token_invalido": return False
            if not data or not data.get('results'):
                logger.info("📭 Fim da busca. Nenhum pedido adicional encontrado.")
                break

            orders = data.get('results', [])
            await self._process_order_batch(orders, credentials)

            total_pedidos_processados += len(orders)
            logger.info(f"🔄 Lote processado. {len(orders)} pedidos. Total acumulado: {total_pedidos_processados}")

            paging = data.get('paging', {})
            offset = paging.get('offset', 0) + paging.get('limit', 50)
            if offset >= paging.get('total', 0): break

        logger.info(f"✅ Busca finalizada. Total de {total_pedidos_processados} pedidos lidos.")
        return True

    # --- MOTOR DE ORQUESTRAÇÃO ---
    async def _processar_sincronizacao(self, company_id: int, days_back: int = None, hours_back: int = None):
        logger.info(f"🎯 Iniciando sincronização ML para empresa {company_id} (dias={days_back}, horas={hours_back})")
        credentials = self._get_company_credentials(company_id)
        if not credentials: return False

        async with aiohttp.ClientSession() as session:
            # Validação proativa do token antes de iniciar a busca massiva
            test_url = f"{self.api_url}/users/me"
            test_response = await self._make_api_request(session, test_url, 'GET', headers={
                "Authorization": f"Bearer {credentials['access_token']}"})

            if test_response == "token_invalido":
                logger.warning("Token existente inválido. Iniciando processo de renovação.")
                new_access, new_refresh = await self._refresh_token(credentials, session)
                if new_access:
                    self._update_company_tokens(company_id, new_access, new_refresh)
                    credentials['access_token'] = new_access
                else:
                    logger.error(f"❌ Sincronização abortada: Falha crítica ao renovar token para empresa {company_id}.")
                    return False

            success = await self._fetch_all_orders_for_company(credentials, session, days_back, hours_back)
            if not success:
                logger.error(f"❌ Sincronização falhou durante a busca de pedidos para empresa {company_id}.")
                return False

        logger.info(f"✅ Sincronização ML concluída para empresa {company_id}.")
        return True


# --- PONTOS DE ENTRADA (CRON JOBS) ---
def sync_full_reconciliation():
    logger.info("CRON JOB: Iniciando fluxo de reconciliação completa (60 dias).")
    app = create_app()
    with app.app_context():
        companies = Company.query.filter_by(ativo=True).all()
        service = MercadoLivreService(app_context=app)
        for company in companies:
            asyncio.run(service._processar_sincronizacao(company.id, days_back=60))
    logger.info("CRON JOB: Fluxo de reconciliação completa finalizado.")


def sync_recent_orders():
    logger.info("CRON JOB: Iniciando fluxo de sincronização de pedidos recentes (2 horas).")
    app = create_app()
    with app.app_context():
        companies = Company.query.filter_by(ativo=True).all()
        service = MercadoLivreService(app_context=app)
        for company in companies:
            asyncio.run(service._processar_sincronizacao(company.id, hours_back=2))
    logger.info("CRON JOB: Fluxo de sincronização de pedidos recentes finalizado.")
