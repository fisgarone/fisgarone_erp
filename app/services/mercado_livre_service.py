# app/services/mercado_livre_service.py - VERSÃO FINAL CORRIGIDA

import asyncio
import aiohttp
import os
from datetime import datetime, timedelta
import pytz
from dateutil import parser
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app
from app.extensions import db
from app.models.company import Company, IntegrationConfig
from app.models.ml_models import VendaML
import logging

logger = logging.getLogger(__name__)


class MercadoLivreService:
    def __init__(self):
        self.api_url = os.environ.get("API_URL", "https://api.mercadolibre.com")
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _get_company_credentials(self, company_id):
        config = IntegrationConfig.query.filter_by(company_id=company_id, ml_ativo=True).first()
        if not config:
            return None
        return {
            'client_id': config.ml_app_id,
            'client_secret': config.ml_client_secret,
            'access_token': config.ml_access_token,
            'refresh_token': config.ml_refresh_token,
            'seller_id': config.ml_seller_id,
            'company_id': company_id
        }

    def _update_company_tokens(self, company_id, access_token, refresh_token):
        try:
            config = IntegrationConfig.query.filter_by(company_id=company_id).first()
            if config:
                config.ml_access_token = access_token
                if refresh_token:
                    config.ml_refresh_token = refresh_token
                config.ml_token_expires = datetime.utcnow() + timedelta(hours=4)
                config.data_atualizacao = datetime.utcnow()
                db.session.commit()
                logger.info(f"Tokens atualizados no DB para empresa {company_id}")
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erro de DB ao atualizar tokens: {e}")

    async def _make_api_request(self, session, url, method='GET', headers=None, data=None, params=None):
        request_headers = self.default_headers.copy()
        if headers:
            request_headers.update(headers)
        try:
            async with session.request(method, url, headers=request_headers, data=data, params=params) as response:
                if 200 <= response.status < 300:
                    return await response.json()
                if response.status in [400, 401, 403]:
                    return {"error": response.status, "body": await response.text()}
                logger.error(f"Erro de API não tratado {response.status}: {await response.text()}")
                return None
        except Exception as e:
            logger.error(f"Exceção na requisição: {e}")
        return None

    async def _refresh_token(self, credentials, session):
        url = f"{self.api_url}/oauth/token"
        payload = {
            'grant_type': 'refresh_token',
            'client_id': credentials['client_id'],
            'client_secret': credentials['client_secret'],
            'refresh_token': credentials['refresh_token']
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        result = await self._make_api_request(session, url, 'POST', headers=headers, data=payload)
        if result and isinstance(result, dict) and "error" not in result:
            return result.get('access_token'), result.get('refresh_token')
        logger.error(f"Falha ao renovar token. Resposta da API: {result}")
        return None, None

    async def _process_single_order(self, order_data, credentials):
        """
        CORREÇÃO CRÍTICA: Converter order_id para string antes de buscar no banco
        """
        try:
            order_id = order_data.get("id")
            # ✅ CORREÇÃO: Converter para string para compatibilidade com VARCHAR
            order_id_str = str(order_id)
            
            for item in order_data.get("order_items", []):
                # Buscar pelo ID convertido para string
                venda = VendaML.query.get(order_id_str) or VendaML(id_pedido=order_id_str)
                venda.company_id = credentials['company_id']
                venda.situacao = order_data.get('status')
                venda.data_venda = parser.parse(order_data.get("date_created")).strftime('%d/%m/%Y')
                venda.quantidade = item.get('quantity')
                venda.preco_unitario = item.get('unit_price')
                venda.mlb = item.get('item', {}).get('id')
                venda.sku = item.get('item', {}).get('seller_sku')
                venda.titulo = item.get('item', {}).get('title')
                venda.taxa_ml = item.get('sale_fee', 0)
                db.session.add(venda)
            db.session.commit()
            logger.debug(f"✅ Pedido {order_id_str} salvo com sucesso")
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Erro ao salvar pedido {order_data.get('id')}: {e}")

    async def _fetch_all_orders_for_company(self, credentials, session, days_back, hours_back):
        headers = {"Authorization": f"Bearer {credentials['access_token']}"}
        now_br = datetime.now(pytz.timezone('America/Sao_Paulo'))
        start_date = now_br - (timedelta(days=days_back) if days_back else timedelta(hours=hours_back or 1))
        start_date_str = start_date.isoformat()
        offset, limit, total_pedidos_processados = 0, 50, 0
        logger.info(f"📦 Buscando pedidos de {start_date_str} para empresa {credentials['company_id']}")

        while True:
            params = {
                'seller': str(credentials['seller_id']),
                'sort': 'date_desc',
                'order.date_created.from': start_date_str,
                'offset': offset,
                'limit': limit
            }
            data = await self._make_api_request(session, f"{self.api_url}/orders/search", 'GET', headers=headers,
                                                params=params)

            if data and isinstance(data, dict) and data.get("error"):
                logger.error(f"Erro ao buscar pedidos: {data}")
                return False

            if not data or not data.get('results'):
                logger.info("📭 Fim da busca. Nenhum pedido adicional encontrado.")
                break

            orders = data.get('results', [])
            await asyncio.gather(*[self._process_single_order(order, credentials) for order in orders])

            total_pedidos_processados += len(orders)
            logger.info(f"🔄 Lote processado. {len(orders)} pedidos. Total acumulado: {total_pedidos_processados}")

            paging = data.get('paging', {})
            offset = paging.get('offset', 0) + paging.get('limit', 50)
            if offset >= paging.get('total', 0):
                break
        logger.info(f"✅ Busca finalizada. Total de {total_pedidos_processados} pedidos lidos.")
        return True

    async def _processar_sincronizacao(self, company_id: int, days_back: int = None, hours_back: int = None):
        logger.info(f"🎯 Iniciando sincronização ML para empresa {company_id}")
        credentials = self._get_company_credentials(company_id)
        if not credentials:
            logger.warning(f"❌ Nenhuma credencial ativa encontrada para empresa {company_id}")
            return

        async with aiohttp.ClientSession() as session:
            test_url = f"{self.api_url}/orders/search"
            test_params = {'seller': str(credentials['seller_id']), 'limit': 0}
            headers = {"Authorization": f"Bearer {credentials['access_token']}"}
            test_response = await self._make_api_request(session, test_url, 'GET', headers=headers,
                                                          params=test_params)

            if test_response and isinstance(test_response, dict) and test_response.get("error"):
                logger.warning(
                    f"Token de acesso inválido ou com permissão negada ({test_response.get('error')}). Tentando renovar...")
                new_access, new_refresh = await self._refresh_token(credentials, session)
                if new_access:
                    self._update_company_tokens(company_id, new_access, new_refresh)
                    credentials['access_token'] = new_access
                else:
                    logger.error(f"❌ Falha crítica ao renovar token para empresa {company_id}. Sincronização abortada.")
                    return

            success = await self._fetch_all_orders_for_company(credentials, session, days_back, hours_back)
            if not success:
                logger.error(f"❌ Sincronização falhou durante a busca de pedidos para empresa {company_id}.")
                return

        logger.info(f"✅ Sincronização ML concluída para empresa {company_id}.")

    def sync_orders(self, company_id: int, days_back: int = 7):
        asyncio.run(self._processar_sincronizacao(company_id, days_back=days_back))
        return {"success": True, "message": f"Sincronização iniciada para empresa {company_id}"}


def sync_full_reconciliation():
    logger.info("CRON JOB: Iniciando fluxo de reconciliação completa (60 dias).")
    companies = Company.query.filter_by(ativo=True).all()
    if not companies:
        logger.warning("Nenhuma empresa ativa encontrada para sincronização.")
        return
    service = MercadoLivreService()
    for company in companies:
        asyncio.run(service._processar_sincronizacao(company.id, days_back=60))
    logger.info("CRON JOB: Fluxo de reconciliação completa finalizado.")


def sync_recent_orders():
    logger.info("CRON JOB: Iniciando fluxo de sincronização de pedidos recentes (2 horas).")
    companies = Company.query.filter_by(ativo=True).all()
    if not companies:
        logger.warning("Nenhuma empresa ativa encontrada para sincronização.")
        return
    service = MercadoLivreService()
    for company in companies:
        asyncio.run(service._processar_sincronizacao(company.id, hours_back=2))
    logger.info("CRON JOB: Fluxo de sincronização de pedidos recentes finalizado.")
