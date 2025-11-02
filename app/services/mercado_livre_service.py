# app/services/mercado_livre_service.py - VERSÃO COM SUPORTE MULTI-CONTA

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
    def __init__(self):
        self.api_url = os.environ.get("API_URL", "https://api.mercadolibre.com")
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _get_company_credentials(self, company_id):
        """Retorna credenciais de UMA conta específica"""
        config = IntegrationConfig.query.filter_by(company_id=company_id, ml_ativo=True).first()
        if not config:
            return None
        return {
            'client_id': config.ml_app_id,
            'client_secret': config.ml_client_secret,
            'access_token': config.ml_access_token,
            'refresh_token': config.ml_refresh_token,
            'seller_id': config.ml_seller_id,
            'company_id': company_id,
            'config_id': config.id
        }

    def _get_all_company_credentials(self, company_id):
        """NOVO: Retorna credenciais de TODAS as contas ativas da empresa"""
        configs = IntegrationConfig.query.filter_by(company_id=company_id, ml_ativo=True).all()
        if not configs:
            return []
        
        credentials_list = []
        for config in configs:
            credentials_list.append({
                'client_id': config.ml_app_id,
                'client_secret': config.ml_client_secret,
                'access_token': config.ml_access_token,
                'refresh_token': config.ml_refresh_token,
                'seller_id': config.ml_seller_id,
                'company_id': company_id,
                'config_id': config.id
            })
        
        logger.info(f"✅ Encontradas {len(credentials_list)} contas ativas para empresa {company_id}")
        return credentials_list

    def _update_company_tokens(self, config_id, access_token, refresh_token):
        """MODIFICADO: Atualiza tokens usando config_id em vez de company_id"""
        try:
            config = IntegrationConfig.query.get(config_id)
            if config:
                config.ml_access_token = access_token
                if refresh_token:
                    config.ml_refresh_token = refresh_token
                config.ml_token_expires = datetime.utcnow() + timedelta(hours=4)
                config.data_atualizacao = datetime.utcnow()
                db.session.commit()
                logger.info(f"Tokens atualizados no DB para config {config_id}")
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
        data = await self._make_api_request(session, url, 'POST', data=payload)
        if data and 'access_token' in data:
            logger.info("✅ Token renovado com sucesso.")
            return data['access_token'], data.get('refresh_token')
        logger.error("❌ Falha ao renovar token.")
        return None, None

    async def _process_single_order(self, order_data, credentials):
        try:
            order_id = order_data.get("id")
            order_id_str = str(order_id)
            venda = VendaML.query.get(order_id_str)

            if not venda:
                venda = VendaML(id_pedido=order_id_str)

            for item in order_data.get('order_items', []):
                preco_unitario = Decimal(item.get('unit_price', '0.0'))
                quantidade = int(item.get('quantity', 1))
                taxa_mercado_livre_unitaria = Decimal(item.get('sale_fee', '0.0'))
                faturamento_total = preco_unitario * quantidade

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

                # ETAPA 1: Calcular taxa_fixa_ml
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

                # ETAPA 2: Calcular comissoes
                comissao_bruta_total = taxa_mercado_livre_unitaria * quantidade
                comissao_real_total = comissao_bruta_total - taxa_fixa_total
                venda.comissoes = comissao_real_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) if comissao_real_total > 0 else Decimal('0.0')

                # ETAPA 3: Calcular comissao_percent
                if faturamento_total > 0:
                    percentual_comissao = (venda.comissoes / faturamento_total) * 100
                    venda.comissao_percent = percentual_comissao.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                else:
                    venda.comissao_percent = Decimal('0.0')

                # ETAPA 4: Calcular frete_seller
                custo_frete_total = Decimal('0.0')
                if preco_unitario >= Decimal('79.00'):
                    custo_frete_total = Decimal('29.00') * quantidade
                venda.frete_seller = custo_frete_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                # ETAPA 5: Calcular custo_operacional_ml
                venda.custo_operacional_ml = (venda.comissoes + venda.taxa_fixa_ml + venda.frete_seller)

                # ETAPA 6: Calcular mc_ml
                venda.mc_ml = faturamento_total - venda.custo_operacional_ml

                db.session.add(venda)

            db.session.commit()

        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Erro ao processar pedido {order_data.get('id')}: {e}")
            logger.exception(e)

    async def _fetch_all_orders_for_company(self, credentials, session, days_back, hours_back):
        headers = {"Authorization": f"Bearer {credentials['access_token']}"}
        now_br = datetime.now(pytz.timezone('America/Sao_Paulo'))
        start_date = now_br - (timedelta(days=days_back) if days_back else timedelta(hours=hours_back or 1))
        start_date_str = start_date.isoformat()
        offset, limit, total_pedidos_processados = 0, 50, 0
        logger.info(f"📦 Buscando pedidos de {start_date_str} para seller {credentials['seller_id']}")

        while True:
            params = {
                'seller': str(credentials['seller_id']),
                'sort': 'date_desc',
                'order.date_created.from': start_date_str,
                'offset': offset,
                'limit': limit
            }
            data = await self._make_api_request(session, f"{self.api_url}/orders/search", 'GET', headers=headers, params=params)

            if data and isinstance(data, dict) and data.get("error"):
                logger.error(f"Erro ao buscar pedidos: {data}")
                return False

            if not data or not data.get('results'):
                logger.info(f"📭 Fim da busca para seller {credentials['seller_id']}")
                break

            orders = data.get('results', [])
            await asyncio.gather(*[self._process_single_order(order, credentials) for order in orders])
            total_pedidos_processados += len(orders)
            offset += limit

        logger.info(f"✅ Total de {total_pedidos_processados} pedidos processados para seller {credentials['seller_id']}")
        return True

    async def _processar_sincronizacao_conta(self, credentials, session, days_back, hours_back):
        """NOVO: Sincroniza UMA conta específica"""
        logger.info(f"🎯 Sincronizando conta {credentials['seller_id']}")
        
        # Testar token
        test_url = f"{self.api_url}/orders/search"
        test_params = {'seller': str(credentials['seller_id']), 'limit': 0}
        headers = {"Authorization": f"Bearer {credentials['access_token']}"}
        test_response = await self._make_api_request(session, test_url, 'GET', headers=headers, params=test_params)

        if test_response and isinstance(test_response, dict) and test_response.get("error"):
            logger.warning(f"Token inválido para seller {credentials['seller_id']}. Tentando renovar...")
            new_access, new_refresh = await self._refresh_token(credentials, session)
            if new_access:
                self._update_company_tokens(credentials['config_id'], new_access, new_refresh)
                credentials['access_token'] = new_access
            else:
                logger.error(f"❌ Falha ao renovar token para seller {credentials['seller_id']}")
                return False

        success = await self._fetch_all_orders_for_company(credentials, session, days_back, hours_back)
        return success

    async def _processar_sincronizacao_todas_contas(self, company_id: int, days_back: int = None, hours_back: int = None):
        """NOVO: Sincroniza TODAS as contas da empresa em paralelo"""
        logger.info(f"🎯 Iniciando sincronização de TODAS as contas ML para empresa {company_id}")
        
        all_credentials = self._get_all_company_credentials(company_id)
        if not all_credentials:
            logger.warning(f"❌ Nenhuma credencial ativa encontrada para empresa {company_id}")
            return

        async with aiohttp.ClientSession() as session:
            # Sincronizar todas as contas em paralelo
            tasks = [self._processar_sincronizacao_conta(cred, session, days_back, hours_back) for cred in all_credentials]
            results = await asyncio.gather(*tasks)
            
            sucesso = sum(results)
            total = len(results)
            logger.info(f"✅ Sincronização concluída: {sucesso}/{total} contas sincronizadas com sucesso")

    def sync_orders(self, company_id: int, days_back: int = 7):
        """Sincroniza TODAS as contas da empresa"""
        asyncio.run(self._processar_sincronizacao_todas_contas(company_id, days_back=days_back))
        return {"success": True, "message": f"Sincronização iniciada para todas as contas da empresa {company_id}"}


def sync_full_reconciliation():
    logger.info("CRON JOB: Iniciando reconciliação completa (60 dias) para TODAS as contas.")
    companies = Company.query.filter_by(ativo=True).all()
    if not companies:
        logger.warning("Nenhuma empresa ativa encontrada.")
        return
    service = MercadoLivreService()
    for company in companies:
        asyncio.run(service._processar_sincronizacao_todas_contas(company.id, days_back=60))
    logger.info("CRON JOB: Reconciliação completa finalizada.")


def sync_recent_orders():
    logger.info("CRON JOB: Iniciando sincronização recente (2 horas) para TODAS as contas.")
    companies = Company.query.filter_by(ativo=True).all()
    if not companies:
        logger.warning("Nenhuma empresa ativa encontrada.")
        return
    service = MercadoLivreService()
    for company in companies:
        asyncio.run(service._processar_sincronizacao_todas_contas(company.id, hours_back=2))
    logger.info("CRON JOB: Sincronização recente finalizada.")
