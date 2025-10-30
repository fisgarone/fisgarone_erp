# app/services/mercado_livre_service.py - VERSÃO FINAL PARA RENDER
import asyncio
import aiohttp
import os
from datetime import datetime, timedelta
import pytz
from dateutil import parser
from sqlalchemy.exc import SQLAlchemyError

# Importa o app factory e as extensões para criar o contexto da aplicação
from app import create_app
from app.extensions import db
from app.models.company import Company, IntegrationConfig
from app.models.ml_models import VendaML, RepasseML, CustoML
import logging

# Configuração básica do logging
logging.basicConfig(level=logging.INFO, format='%(asctime )s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MercadoLivreService:
    """
    Serviço para integração com a API do Mercado Livre, otimizado para
    execução em ambiente de produção (Render) com múltiplos fluxos de sincronização.
    """

    def __init__(self, app_context=None):
        self.max_concurrent_requests = 15
        self.api_url = os.environ.get("API_URL", "https://api.mercadolibre.com")
        # Se um contexto de app for passado, use-o. Senão, crie um novo.
        # Isso permite que o serviço seja usado tanto em rotas Flask quanto em scripts.
        if app_context:
            self.app = app_context
        else:
            self.app = create_app()

    def _get_company_credentials(self, company_id):
        """Obtém credenciais da empresa do banco de dados dentro de um contexto de aplicação."""
        with self.app.app_context():
            # A query agora é executada dentro do contexto, garantindo acesso ao 'db'
            config = IntegrationConfig.query.filter_by(company_id=company_id, ml_ativo=True).first()
            if not config:
                logger.error(f"Configuração ML ativa não encontrada para empresa {company_id}")
                return None

            company = Company.query.get(company_id)
            if not company:
                logger.error(f"Empresa {company_id} não encontrada para a configuração ML")
                return None

            return {
                'nome': company.nome_fantasia,
                'client_id': config.ml_app_id,
                'client_secret': config.ml_client_secret,
                'access_token': config.ml_access_token,
                'refresh_token': config.ml_refresh_token,
                'seller_id': config.ml_seller_id,  # Assumindo que este campo existe
                'company_id': company_id
            }

    def _update_company_tokens(self, company_id, access_token, refresh_token):
        """Atualiza tokens no banco de dados dentro de um contexto de aplicação."""
        with self.app.app_context():
            try:
                config = IntegrationConfig.query.filter_by(company_id=company_id).first()
                if config:
                    config.ml_access_token = access_token
                    config.ml_refresh_token = refresh_token
                    config.ml_token_expires = datetime.utcnow() + timedelta(hours=4)  # Estima a expiração
                    config.updated_at = datetime.utcnow()
                    db.session.commit()
                    logger.info(f"Tokens atualizados com sucesso para empresa {company_id}")
            except SQLAlchemyError as e:
                db.session.rollback()
                logger.error(f"Erro de banco de dados ao atualizar tokens para empresa {company_id}: {e}")

    async def _refresh_token(self, client_id, client_secret, refresh_token, session):
        """Renova token de acesso de forma assíncrona."""
        url = f"{self.api_url}/oauth/token"
        payload = {
            'grant_type': 'refresh_token',
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token
        }
        try:
            async with session.post(url, data=payload) as response:
                response.raise_for_status()  # Lança exceção para status de erro (4xx, 5xx)
                new_tokens = await response.json()
                logger.info("Token de acesso renovado com sucesso.")
                return new_tokens.get('access_token'), new_tokens.get('refresh_token')
        except aiohttp.ClientError as e:
            logger.error(f"Erro de cliente HTTP ao renovar token: {e}")
            return None, None
        except Exception as e:
            logger.error(f"Exceção inesperada ao renovar token: {e}")
            return None, None

    async def _processar_sincronizacao(self, company_id: int, days_back: int = None, hours_back: int = None):
        """
        Motor central de sincronização, parametrizado por dias ou horas.
        """
        logger.info(f"🎯 Iniciando sincronização ML para empresa {company_id} (dias={days_back}, horas={hours_back})")
        credentials = self._get_company_credentials(company_id)
        if not credentials:
            return False

        async with aiohttp.ClientSession() as session:
            new_access, new_refresh = await self._refresh_token(
                credentials['client_id'], credentials['client_secret'], credentials['refresh_token'], session
            )
            if new_access and new_refresh:
                self._update_company_tokens(company_id, new_access, new_refresh)
                credentials['access_token'] = new_access
            else:
                logger.warning(f"⚠️  Falha ao renovar token. Usando token existente para {credentials['nome']}.")

            if not credentials.get('access_token'):
                logger.error(f"❌ Sincronização abortada: Access token inválido para {credentials['nome']}.")
                return False

            await self._fetch_all_orders_for_company(credentials, session, days_back, hours_back)

        # Executa os cálculos financeiros dentro do contexto da aplicação
        with self.app.app_context():
            await self._calcular_financeiro_completo(credentials['nome'])
            await self._processar_repasses(credentials['nome'])

        logger.info(f"✅ Sincronização ML concluída para empresa {company_id}.")
        return True

    async def _fetch_all_orders_for_company(self, credentials, session, days_back, hours_back):
        """Busca e processa todos os pedidos para uma empresa."""
        headers = {"Authorization": f"Bearer {credentials['access_token']}"}

        # Define o período de busca
        now_br = datetime.now(pytz.timezone('America/Sao_Paulo'))
        if days_back:
            start_date = now_br - timedelta(days=days_back)
        elif hours_back:
            start_date = now_br - timedelta(hours=hours_back)
        else:  # Fallback seguro
            start_date = now_br - timedelta(days=1)

        # Formato de data exigido pela API do ML
        start_date_str = start_date.isoformat()

        logger.info(f"📦 Buscando pedidos de {start_date_str} para {credentials['nome']}")

        offset = 0
        limit = 50
        total_pedidos_processados = 0

        while True:
            params = {
                'seller_id': credentials['seller_id'],
                'sort': 'date_desc',
                'order.date_created.from': start_date_str,
                'offset': offset,
                'limit': limit
            }
            try:
                async with session.get(f"{self.api_url}/orders/search", headers=headers, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
                    orders = data.get('results', [])

                    if not orders:
                        logger.info(f"📭 Fim da busca. Nenhum pedido adicional encontrado para {credentials['nome']}.")
                        break

                    # Usando asyncio.gather para processar pedidos em paralelo
                    tasks = [self._process_single_order(order, credentials, session) for order in orders]
                    await asyncio.gather(*tasks)

                    total_pedidos_processados += len(orders)
                    logger.info(
                        f"🔄 Lote processado. {len(orders)} pedidos. Total acumulado: {total_pedidos_processados}")

                    paging = data.get('paging', {})
                    offset = paging.get('offset', 0) + paging.get('limit', 50)
                    total_api = paging.get('total', 0)

                    if offset >= total_api:
                        break
            except aiohttp.ClientError as e:
                logger.error(f"❌ Erro de API ao buscar pedidos para {credentials['nome']}: {e}")
                break
            except Exception as e:
                logger.error(f"❌ Exceção inesperada durante a busca de pedidos: {e}")
                break

        logger.info(
            f"✅ Busca finalizada para {credentials['nome']}. Total de {total_pedidos_processados} pedidos processados.")

    async def _process_single_order(self, order_data, credentials, session):
        """Processa um único pedido e o salva no banco de dados."""
        order_id = order_data.get("id")
        with self.app.app - context():
            try:
                # Lógica para processar e salvar cada pedido (similar à sua, mas dentro do contexto)
                # ... (aqui entraria sua lógica detalhada de extração de dados do 'order_data')

                # Exemplo simplificado:
                venda_existente = VendaML.query.get(order_id)
                if not venda_existente:
                    venda_existente = VendaML(id_pedido=order_id)

                venda_existente.conta = credentials['nome']
                venda_existente.situacao = order_data.get('status')
                # ... preencher todos os outros campos

                db.session.add(venda_existente)
                db.session.commit()
                logger.debug(f"Pedido {order_id} salvo/atualizado.")

            except SQLAlchemyError as e:
                db.session.rollback()
                logger.error(f"Erro de banco de dados ao processar pedido {order_id}: {e}")
            except Exception as e:
                logger.error(f"Erro inesperado ao processar pedido {order_id}: {e}")

    # ... (seus métodos _traduzir_logistica, _traduzir_situacao, _get_shipment_details,
    #      _calcular_financeiro_completo, _processar_repasses devem ser mantidos aqui,
    #      garantindo que as operações de DB estejam dentro de um `with self.app.app_context():`)


# --- PONTOS DE ENTRADA PARA OS CRON JOBS ---

def sync_full_reconciliation():
    """Ponto de entrada para o Cron Job de reconciliação completa."""
    logger.info("CRON JOB: Iniciando fluxo de reconciliação completa (60 dias).")
    app = create_app()
    with app.app_context():
        # Aqui você buscaria todas as empresas ativas
        companies = Company.query.filter_by(ativo=True).all()
        service = MercadoLivreService(app_context=app)
        for company in companies:
            asyncio.run(service._processar_sincronizacao(company.id, days_back=60))
    logger.info("CRON JOB: Fluxo de reconciliação completa finalizado.")


def sync_recent_orders():
    """Ponto de entrada para o Cron Job de sincronização de pedidos recentes."""
    logger.info("CRON JOB: Iniciando fluxo de sincronização de pedidos recentes (2 horas).")
    app = create_app()
    with app.app_context():
        companies = Company.query.filter_by(ativo=True).all()
        service = MercadoLivreService(app_context=app)
        for company in companies:
            asyncio.run(service._processar_sincronizacao(company.id, hours_back=2))
    logger.info("CRON JOB: Fluxo de sincronização de pedidos recentes finalizado.")

