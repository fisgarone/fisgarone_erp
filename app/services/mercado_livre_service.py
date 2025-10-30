# app/services/mercado_livre_service.py - IMPORTAÇÃO CORRIGIDA
import asyncio
import aiohttp
import os
from datetime import datetime, timedelta

import pytz
from dateutil import parser
from sqlalchemy import text
from app.extensions import db
# IMPORTAR DIRETAMENTE - NÃO USAR from app.models import ...
from app.models.company import Company, IntegrationConfig
from app.models.ml_models import VendaML, RepasseML, CustoML
import logging

logger = logging.getLogger(__name__)

class MercadoLivreService:
    def __init__(self):
        self.max_concurrent_requests = 15
        self.days_to_fetch = 60

    def _get_company_credentials(self, company_id):
        """Obtém credenciais da empresa do banco de dados"""
        company = Company.query.get(company_id)
        if not company:
            logger.error(f"Empresa {company_id} não encontrada")
            return None

        config = IntegrationConfig.query.filter_by(
            company_id=company_id,
            platform='mercado_livre'
        ).first()

        if not config:
            logger.error(f"Configuração ML não encontrada para empresa {company_id}")
            return None

        return {
            'nome': company.nome_fantasia,
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'access_token': config.access_token,
            'refresh_token': config.refresh_token,
            'seller_id': config.seller_id,
            'company_id': company_id
        }

    # ... resto do código permanece igual ...

    def _update_company_tokens(self, company_id, access_token, refresh_token):
        """Atualiza tokens no banco de dados"""
        config = IntegrationConfig.query.filter_by(
            company_id=company_id,
            platform='mercado_livre'
        ).first()

        if config:
            config.access_token = access_token
            config.refresh_token = refresh_token
            config.updated_at = datetime.utcnow()
            db.session.commit()
            logger.info(f"Tokens atualizados para empresa {company_id}")

    async def refresh_token(self, client_id, client_secret, refresh_token, api_url, session):
        """Renova token de acesso"""
        url = f"{api_url}/oauth/token"
        data = {
            'grant_type': 'refresh_token',
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token
        }

        try:
            async with session.post(url, data=data) as response:
                if response.status == 200:
                    new_tokens = await response.json()
                    return new_tokens.get('access_token'), new_tokens.get('refresh_token')
                else:
                    error_text = await response.text()
                    logger.error(f"Erro ao atualizar token: {response.status} - {error_text}")
                    return None, None
        except Exception as e:
            logger.error(f"Erro ao tentar atualizar token: {e}")
            return None, None

    async def obter_pedidos_automatico(self, company_id):
        """Função principal para obter pedidos"""
        logger.info(f"🎯 Iniciando sincronização ML para empresa {company_id}")

        credentials = self._get_company_credentials(company_id)
        if not credentials:
            return False

        api_url = os.getenv("API_URL", "https://api.mercadolibre.com")

        async with aiohttp.ClientSession() as session:
            # Verificar e renovar token se necessário
            new_access, new_refresh = await self.refresh_token(
                credentials['client_id'],
                credentials['client_secret'],
                credentials['refresh_token'],
                api_url,
                session
            )

            if new_access and new_refresh:
                logger.info(f"🔄 Tokens renovados para {credentials['nome']}")
                self._update_company_tokens(company_id, new_access, new_refresh)
                credentials['access_token'] = new_access
            else:
                logger.warning(f"⚠️ Usando token existente para {credentials['nome']}")

            # Buscar pedidos
            success = await self._fetch_orders_for_company(
                credentials['access_token'],
                credentials['seller_id'],
                api_url,
                session,
                credentials['nome'],
                credentials['company_id']
            )

            if success:
                logger.info(f"✅ Pedidos processados para {credentials['nome']}")
                await self._calcular_financeiro_completo(credentials['nome'])
                await self._processar_repasses(credentials['nome'])

            return success

    async def _fetch_orders_for_company(self, access_token, seller_id, api_url, session, conta_nome, company_id):
        """Busca pedidos para uma empresa específica"""
        headers = {"Authorization": f"Bearer {access_token}"}
        offset = 0
        limit = 50

        start_date = datetime.now(pytz.timezone('America/Sao_Paulo')) - timedelta(days=self.days_to_fetch)
        start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%S%z")

        logger.info(f"📦 Buscando pedidos de {start_date_str} para {conta_nome}")

        total_pedidos = 0

        while True:
            url = f"{api_url}/orders/search?seller={seller_id}&date_created.from={start_date_str}&offset={offset}&limit={limit}"

            try:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        orders = data.get('results', [])
                        total = data.get('paging', {}).get('total', 0)

                        if not orders:
                            logger.info(f"📭 Nenhum pedido encontrado para {conta_nome}")
                            break

                        # Processar lote de pedidos
                        for pedido in orders:
                            await self._process_single_order(pedido, access_token, api_url, session, conta_nome,
                                                             company_id)
                            total_pedidos += 1

                        logger.info(f"🔄 Processados {len(orders)} pedidos. Total: {total_pedidos}")

                        offset += limit
                        if offset >= total:
                            break
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Erro API ML: {response.status} - {error_text}")
                        break
            except Exception as e:
                logger.error(f"❌ Erro ao buscar pedidos: {e}")
                break

        logger.info(f"✅ Finalizada busca para {conta_nome}. Total: {total_pedidos} pedidos")
        return True

    async def _process_single_order(self, pedido, access_token, api_url, session, conta_nome, company_id):
        """Processa um pedido individual usando SQLAlchemy"""
        try:
            order_id = pedido.get("id", "")
            date_created = pedido.get("date_created", "")

            # Converter data para formato BR
            date_created_br = ""
            if date_created:
                try:
                    date_created_obj = parser.parse(date_created)
                    date_created_br = date_created_obj.strftime("%d/%m/%Y")
                except Exception:
                    date_created_br = date_created

            cancellations = "cancelled" if pedido.get("status") == "cancelled" else "active"
            shipment_id = pedido.get('shipping', {}).get('id', "")
            buyer_id = pedido.get('buyer', {}).get('id', "")

            for item in pedido.get("order_items", []):
                unit_price = float(item.get("unit_price", 0))
                quantity = int(item.get("quantity", 0))
                sale_fee = float(item.get("sale_fee", 0))
                title = item.get("item", {}).get("title", "")
                mlb = item.get("item", {}).get("id", "")
                sku = item.get("item", {}).get("seller_sku", "")

                # Obter detalhes do envio
                envio_details = await self._get_shipment_details(access_token, shipment_id, api_url, session)

                # Cálculo de taxas (do seu código original)
                mlb_taxa_fixa_um_real = ["MLB3776836339", "MLB3804566539", "MLB5116841236"]
                taxa_fixa_ml = (1 if mlb in mlb_taxa_fixa_um_real else 6) * quantity if unit_price < 79 else 0
                comissoes = max(0, (sale_fee * quantity) - taxa_fixa_ml)

                # Buscar ou criar registro usando SQLAlchemy
                venda = VendaML.query.filter_by(id_pedido=order_id).first()
                if not venda:
                    venda = VendaML(id_pedido=order_id)

                # Atualizar dados
                venda.preco_unitario = unit_price
                venda.quantidade = quantity
                venda.data_venda = date_created_br
                venda.taxa_mercado_livre = sale_fee
                venda.frete = envio_details.get("total_shipping_cost", 0) if envio_details else 0
                venda.conta = conta_nome
                venda.cancelamentos = cancellations
                venda.titulo = title
                venda.mlb = mlb
                venda.sku = sku
                venda.codigo_envio = shipment_id
                venda.comprador = buyer_id
                venda.taxa_fixa_ml = taxa_fixa_ml
                venda.comissoes = comissoes

                if envio_details:
                    venda.modo_envio = envio_details.get("shipping_mode", "")
                    venda.tipo_logistica = self._traduzir_logistica(envio_details.get("logistic_type", ""))
                    venda.situacao = self._traduzir_situacao(envio_details.get("status", ""))
                    venda.custo_total_frete = envio_details.get("total_shipping_cost", 0)
                    venda.situacao_entrega = envio_details.get("delivery_status", "")

                db.session.add(venda)

            db.session.commit()
            logger.debug(f"✅ Pedido {order_id} salvo no PostgreSQL")

        except Exception as e:
            logger.error(f"❌ Erro ao processar pedido {order_id}: {e}")
            db.session.rollback()

    def _traduzir_logistica(self, logistic_type):
        """Traduz tipo de logística - do seu código original"""
        if not logistic_type:
            return ""

        logistic_type = logistic_type.lower()
        if "fulfillment" in logistic_type:
            return "Full"
        elif "xd_drop_off" in logistic_type:
            return "Ponto de Coleta"
        elif "self_service" in logistic_type:
            return "Flex"
        return logistic_type

    def _traduzir_situacao(self, status):
        """Traduz situação do pedido - do seu código original"""
        if not status:
            return "Pendente"

        status = status.lower()
        if "ready_to_ship" in status:
            return "Pronto para Envio"
        elif "shipped" in status:
            return "Enviado"
        elif "cancelled" in status:
            return "Cancelado"
        elif "pending" in status:
            return "Pendente"
        elif "delivered" in status:
            return "Entregue"
        return status

    async def _get_shipment_details(self, access_token, shipment_id, api_url, session):
        """Obtém detalhes do envio"""
        if not shipment_id:
            return None

        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"{api_url}/shipments/{shipment_id}"

        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    shipment = await response.json()
                    return {
                        "total_shipping_cost": float(shipment.get("shipping_option", {}).get("cost", 0)),
                        "logistic_type": shipment.get("logistic_type", ""),
                        "status": shipment.get("status", ""),
                        "shipping_mode": shipment.get("shipping_mode", ""),
                        "delivery_status": shipment.get("tracking", {}).get("status", "")
                    }
                else:
                    logger.warning(f"⚠️ Erro ao buscar envio {shipment_id}: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"❌ Erro ao obter envio {shipment_id}: {e}")
            return None

    async def _calcular_financeiro_completo(self, conta_nome):
        """Executa cálculos financeiros - VERSÃO INICIAL (depois completo seus cálculos)"""
        try:
            logger.info(f"🧮 Iniciando cálculos financeiros para {conta_nome}")

            # Cálculo básico de lucro - DEPOIS INSERIMOS SEUS CÁLCULOS COMPLEXOS
            vendas = VendaML.query.filter_by(conta=conta_nome).all()

            for venda in vendas:
                total_venda = float(venda.preco_unitario or 0) * (venda.quantidade or 0)
                custo_total = float(venda.comissoes or 0) + float(venda.taxa_fixa_ml or 0)
                venda.lucro_real = total_venda - custo_total
                venda.lucro_real_percent = (venda.lucro_real / total_venda * 100) if total_venda > 0 else 0

            db.session.commit()
            logger.info(f"✅ Cálculos financeiros básicos concluídos para {conta_nome}")

        except Exception as e:
            logger.error(f"❌ Erro nos cálculos financeiros: {e}")
            db.session.rollback()

    async def _processar_repasses(self, conta_nome):
        """Processa repasses - VERSÃO INICIAL"""
        try:
            logger.info(f"💰 Processando repasses para {conta_nome}")

            # Limpar repasses existentes da conta
            RepasseML.query.filter_by(conta=conta_nome).delete()

            # Buscar vendas da conta
            vendas = VendaML.query.filter_by(conta=conta_nome).all()

            for venda in vendas:
                repasse = RepasseML()
                repasse.id_pedido = venda.id_pedido
                repasse.preco_unitario = venda.preco_unitario
                repasse.data_venda = venda.data_venda
                repasse.quantidade = venda.quantidade
                repasse.tipo_logistica = venda.tipo_logistica
                repasse.situacao = venda.situacao
                repasse.taxa_fixa_ml = venda.taxa_fixa_ml
                repasse.comissoes = venda.comissoes
                repasse.conta = venda.conta

                # Cálculos básicos - DEPOIS INSERIMOS SUA LÓGICA COMPLETA
                total_venda = float(venda.preco_unitario or 0) * (venda.quantidade or 0)
                frete_seller = float(venda.custo_total_frete or 0) if float(venda.preco_unitario or 0) >= 79 else 0
                total_custo = float(venda.taxa_fixa_ml or 0) + float(venda.comissoes or 0) + frete_seller

                repasse.frete_seller = frete_seller
                repasse.total_venda = total_venda
                repasse.total_custo = total_custo
                repasse.valor_repasse = total_venda - total_custo

                db.session.add(repasse)

            db.session.commit()
            logger.info(f"✅ Repasses processados para {conta_nome}: {len(vendas)} registros")

        except Exception as e:
            logger.error(f"❌ Erro ao processar repasses: {e}")
            db.session.rollback()


# Instância global do serviço
mercado_livre_service = MercadoLivreService()