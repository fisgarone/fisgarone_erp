# app/services/mercado_livre_service.py - VERSÃO FINAL E CORRETA

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
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)


class MercadoLivreService:
    # REVISÃO: Estrutura original mantida.
    def __init__(self):
        self.api_url = os.environ.get("API_URL", "https://api.mercadolibre.com")
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    # REVISÃO: Estrutura original mantida.
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

    # REVISÃO: Estrutura original mantida.
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

    # REVISÃO: Estrutura original mantida.
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

    # REVISÃO: Estrutura original mantida.
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

    # REVISÃO: Função reescrita para implementar as 6 etapas da lógica de custos do canal.
    async def _process_single_order(self, order_data, credentials):
        try:
            order_id_str = str(order_data.get("id"))

            for item in order_data.get("order_items", []):
                venda = VendaML.query.get(order_id_str) or VendaML(id_pedido=order_id_str)

                # --- DADOS DE ENTRADA ---
                preco_unitario = Decimal(item.get('unit_price', '0.0'))
                quantidade = int(item.get('quantity', 1))
                taxa_mercado_livre_unitaria = Decimal(item.get('sale_fee', '0.0'))  # Custo bruto unitário da API
                faturamento_total = preco_unitario * quantidade

                # --- POPULANDO DADOS BÁSICOS ---
                venda.company_id = credentials['company_id']
                venda.situacao = order_data.get('status')
                venda.data_venda = parser.parse(order_data.get("date_created")).strftime('%d/%m/%Y')
                venda.quantidade = quantidade
                venda.preco_unitario = preco_unitario
                venda.mlb = item.get('item', {}).get('id')
                venda.sku = item.get('item', {}).get('seller_sku')
                venda.titulo = item.get('item', {}).get('title')
                venda.conta = credentials.get('seller_id')
                venda.data_atualizacao = datetime.utcnow()
                venda.taxa_mercado_livre = taxa_mercado_livre_unitaria

                # --- EXECUÇÃO DA LÓGICA DE CÁLCULO (6 ETAPAS) ---

                # ETAPA 1: Calcular `taxa_fixa_ml`
                taxa_fixa_unitaria = Decimal('0.0')
                if preco_unitario < Decimal('79.00'):
                    if Decimal('50.00') <= preco_unitario < Decimal('79.00'):
                        taxa_fixa_unitaria = Decimal('6.75')
                    elif Decimal('29.00') <= preco_unitario < Decimal('50.00'):
                        taxa_fixa_unitaria = Decimal('6.50')
                    elif Decimal('12.50') <= preco_unitario < Decimal('29.00'):
                        taxa_fixa_unitaria = Decimal('6.25')
                taxa_fixa_total = taxa_fixa_unitaria * quantidade
                venda.taxa_fixa_ml = taxa_fixa_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                # ETAPA 2: Calcular `comissoes` (Comissão Real)
                comissao_bruta_total = taxa_mercado_livre_unitaria * quantidade
                comissao_real_total = comissao_bruta_total - taxa_fixa_total
                venda.comissoes = comissao_real_total.quantize(Decimal('0.01'),
                                                               rounding=ROUND_HALF_UP) if comissao_real_total > 0 else Decimal(
                    '0.0')

                # ETAPA 3: Calcular `comissao_percent`
                if faturamento_total > 0:
                    percentual_comissao = (venda.comissoes / faturamento_total) * 100
                    venda.comissao_percent = percentual_comissao.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                else:
                    venda.comissao_percent = Decimal('0.0')

                # ETAPA 4: Calcular `frete_seller`
                custo_frete_total = Decimal('0.0')
                if preco_unitario >= Decimal('79.00'):
                    custo_frete_total = Decimal('29.00') * quantidade
                venda.frete_seller = custo_frete_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                # ETAPA 5: Calcular `custo_operacional_ml`
                venda.custo_operacional_ml = (venda.comissoes + venda.taxa_fixa_ml + venda.frete_seller)

                # ETAPA 6: Calcular `mc_ml` (Margem de Contribuição do Canal)
                venda.mc_ml = faturamento_total - venda.custo_operacional_ml

                # REVISÃO: A coluna `lucro_real` não será mais tocada por esta lógica,
                # para manter a integridade dos dados e evitar confusão.
                # O frontend será ajustado para usar `mc_ml`.

                db.session.add(venda)

            db.session.commit()

        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Erro ao processar e salvar pedido {order_data.get('id')}: {e}")
            logger.exception(e)

    # REVISÃO: Estrutura original mantida.
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

    # REVISÃO: Estrutura original mantida.
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

    # REVISÃO: Estrutura original mantida.
    def sync_orders(self, company_id: int, days_back: int = 7):
        asyncio.run(self._processar_sincronizacao(company_id, days_back=days_back))
        return {"success": True, "message": f"Sincronização iniciada para empresa {company_id}"}


# REVISÃO: Estrutura original mantida.
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


# REVISÃO: Estrutura original mantida.
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
