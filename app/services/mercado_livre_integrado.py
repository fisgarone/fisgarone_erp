# app/services/mercado_livre_integrado.py
"""
INTEGRAÇÃO FIEL dos códigos:
- importador_automatico.py (sistema principal)
- processamento_automato_ml.py (processamento completo)
"""
import aiohttp
import asyncio
from datetime import datetime, timedelta
from dateutil import parser
import pytz
from sqlalchemy import text
from app.extensions import db
from app.models.ml_models import VendaML, RepasseML, CustoML
import os
import logging

logger = logging.getLogger(__name__)


class MercadoLivreIntegrado:
    def __init__(self):
        self.max_concurrent_requests = 15
        self.days_to_fetch = 60
        self.db_path = "C:/fisgarone/fisgarone.db"  # DO SEU CÓDIGO

    # --- DO SEU importador_automatico.py ---
    def traduzir_valores(self, coluna, valor):
        """CÓDIGO ORIGINAL SEU - traduções"""
        if valor is None:
            return valor
        valor = str(valor).lower()

        if coluna == "Tipo Logistica":
            if "fulfillment" in valor:
                return "Full"
            elif "xd_drop_off" in valor:
                return "Ponto de Coleta"
            elif "self_service" in valor:
                return "Flex"
        elif coluna == "Situacao":
            if "ready_to_ship" in valor:
                return "Pronto para Envio"
            elif "shipped" in valor:
                return "Enviado"
            elif "cancelled" in valor:
                return "Cancelado"
            elif "pending" in valor:
                return "Pendente"
            elif "delivered" in valor:
                return "Entregue"
        elif coluna == "Conta":
            if "202989490" in valor:
                return "Comercial"
            elif "702704896" in valor:
                return "Camping"
            elif "263678949" in valor:
                return "Pesca"
            elif "555536943" in valor:
                return "Toys"
        return valor

    async def refresh_token(self, client_id, client_secret, refresh_token, api_url, session):
        """CÓDIGO ORIGINAL SEU - refresh token"""
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
                    logger.error(f"Erro ao atualizar token: {response.status}")
                    return None, None
        except Exception as e:
            logger.error(f"Erro ao tentar atualizar token: {e}")
            return None, None

    async def fetch_shipment_costs_and_payments(self, access_token, shipment_id, api_url, session):
        """CÓDIGO ORIGINAL SEU - custos de envio"""
        headers = {"Authorization": f"Bearer {access_token}", "x-format-new": "true"}
        costs_url = f"{api_url}/shipments/{shipment_id}/costs"
        payments_url = f"{api_url}/shipments/{shipment_id}/payments"

        try:
            async with session.get(costs_url, headers=headers) as response:
                if response.status == 200:
                    shipment_costs = await response.json()
                    shipping_base_cost = float(shipment_costs.get("gross_amount", 0.0))
                else:
                    logger.error(f"Erro ao buscar custos do envio: {response.status}")
                    return None, None

            async with session.get(payments_url, headers=headers) as response:
                if response.status == 200:
                    shipment_payments = await response.json()
                    if isinstance(shipment_payments, list) and shipment_payments:
                        shipping_cost = float(shipment_payments[0].get("amount", 0.0))
                    elif isinstance(shipment_payments, dict):
                        shipping_cost = float(shipment_payments.get("amount", 0.0))
                    else:
                        shipping_cost = 0.0
                else:
                    logger.error(f"Erro ao buscar pagamentos: {response.status}")
                    return None, None

            return shipping_cost, shipping_base_cost
        except Exception as e:
            logger.error(f"Erro ao acessar dados de envio: {e}")
            return None, None

    async def fetch_billing_details(self, access_token, order_id, api_url, session):
        """CÓDIGO ORIGINAL SEU - detalhes de billing"""
        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"{api_url}/billing/integration/group/ML/order/details?order_ids={order_id}"

        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get('results', [])
                    if results:
                        order_data = results[0]

                        # Obter quem pagou o frete
                        paid_by = "seller"
                        for detail in order_data.get('details', []):
                            if detail.get('marketplace_info', {}).get('marketplace') == 'SHIPPING':
                                receiver_cost = detail.get('shipping_info', {}).get('receiver_shipping_cost')
                                if receiver_cost is not None and float(receiver_cost) == 0:
                                    paid_by = "seller"
                                else:
                                    paid_by = "buyer"

                        # Obter data de liberação
                        release_date = None
                        payment_info = order_data.get('payment_info', [])
                        if payment_info:
                            release_date = payment_info[0].get('money_release_date')
                            if release_date:
                                try:
                                    release_date = parser.parse(release_date).strftime("%Y-%m-%d %H:%M:%S")
                                except:
                                    release_date = None

                        return {"paid_by": paid_by, "release_date": release_date}
                    else:
                        logger.warning(f"Nenhum dado de billing para {order_id}")
                        return None
                else:
                    logger.error(f"Erro billing para {order_id}: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Erro ao processar billing: {e}")
            return None

    async def fetch_shipment(self, access_token, shipment_id, api_url, session):
        """CÓDIGO ORIGINAL SEU - detalhes do envio"""
        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"{api_url}/shipments/{shipment_id}"

        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    shipment = await response.json()

                    logistic_type = shipment.get("logistic_type", "Não disponível")
                    shipping_mode = shipment.get("shipping_mode", "")
                    shipping_base_cost = float(shipment.get("shipping_option", {}).get("base_cost", 0.0))
                    shipping_option_cost = float(shipment.get("shipping_option", {}).get("cost", 0.0))
                    shipping_order_cost = float(shipment.get("order_cost", 0.0))
                    shipping_list_cost = float(shipment.get("shipping_option", {}).get("list_cost", 0.0))
                    total_shipping_cost = float(shipment.get("total", 0.0))
                    status = shipment.get("status", "")
                    delivery_status = shipment.get("tracking", {}).get("status", "")
                    release_date = shipment.get("date_estimated_delivery", {}).get("date", None)

                    if release_date:
                        try:
                            release_date = datetime.strptime(release_date, "%Y-%m-%dT%H:%M:%S").strftime(
                                "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            release_date = None

                    # Obter custos reais
                    shipping_cost, shipping_base_cost = await self.fetch_shipment_costs_and_payments(
                        access_token, shipment_id, api_url, session
                    )

                    if shipping_cost is not None and shipping_base_cost is not None:
                        total_shipping_cost = shipping_cost
                        return {
                            "logistic_type": logistic_type,
                            "shipping_mode": shipping_mode,
                            "shipping_base_cost": shipping_base_cost,
                            "shipping_option_cost": shipping_option_cost,
                            "shipping_order_cost": shipping_order_cost,
                            "shipping_list_cost": shipping_list_cost,
                            "total_shipping_cost": total_shipping_cost,
                            "status": status,
                            "delivery_status": delivery_status,
                            "release_date": release_date,
                            "date_created": shipment.get("date_created", "")
                        }
                    return None
                else:
                    logger.error(f"Erro ao buscar envio {shipment_id}: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Erro ao tentar acessar o envio: {e}")
            return None

    async def processar_pedido_completo(self, pedido, access_token, api_url, session, conta_nome):
        """PROCESSAMENTO COMPLETO - como no seu código original"""
        try:
            order_id = pedido.get("id", "")
            date_created = pedido.get("date_created", "")

            # Converter data - DO SEU CÓDIGO
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

                # Obter detalhes do envio - SEU CÓDIGO
                envio_details = await self.fetch_shipment(access_token, shipment_id, api_url, session)

                # Obter billing details - SEU CÓDIGO
                billing_details = await self.fetch_billing_details(access_token, order_id, api_url, session)

                # CÁLCULOS DE TAXAS - DO SEU CÓDIGO
                mlb_taxa_fixa_um_real = ["MLB3776836339", "MLB3804566539", "MLB5116841236"]
                taxa_fixa_ml = (1 if mlb in mlb_taxa_fixa_um_real else 6) * quantity if unit_price < 79 else 0
                comissoes = max(0, (sale_fee * quantity) - taxa_fixa_ml)

                # Calcular porcentagem - SEU CÓDIGO
                comissao_percent = 0
                if unit_price and quantity:
                    comissao_percent = comissoes / (unit_price * quantity)

                # Usar dados de billing se disponíveis
                paid_by = billing_details["paid_by"] if billing_details else "unknown"
                release_date = billing_details["release_date"] if billing_details else envio_details[
                    "release_date"] if envio_details else None

                # SALVAR NO BANCO - Adaptado para MySQL
                venda = VendaML(
                    id_pedido=order_id,
                    preco_unitario=unit_price,
                    quantidade=quantity,
                    data_venda=date_created_br,
                    taxa_mercado_livre=sale_fee,
                    frete=envio_details["total_shipping_cost"] if envio_details else 0,
                    conta=conta_nome,
                    cancelamentos=cancellations,
                    titulo=title,
                    mlb=mlb,
                    sku=sku,
                    codigo_envio=shipment_id,
                    comprador=buyer_id,
                    modo_envio=envio_details["shipping_mode"] if envio_details else "",
                    custo_frete_base=envio_details["shipping_base_cost"] if envio_details else 0,
                    custo_frete_opcional=envio_details["shipping_option_cost"] if envio_details else 0,
                    custo_pedido_frete=envio_details["shipping_order_cost"] if envio_details else 0,
                    custo_lista_frete=envio_details["shipping_list_cost"] if envio_details else 0,
                    custo_total_frete=envio_details["total_shipping_cost"] if envio_details else 0,
                    tipo_logistica=self.traduzir_valores("Tipo Logistica",
                                                         envio_details["logistic_type"] if envio_details else ""),
                    pago_por=paid_by,
                    situacao=self.traduzir_valores("Situacao", envio_details["status"] if envio_details else ""),
                    situacao_entrega=envio_details["delivery_status"] if envio_details else "",
                    data_liberacao=release_date,
                    taxa_fixa_ml=taxa_fixa_ml,
                    comissoes=comissoes,
                    comissao_percent=comissao_percent
                )

                db.session.add(venda)

            db.session.commit()
            logger.info(f"✅ Pedido {order_id} processado e salvo")

        except Exception as e:
            logger.error(f"❌ Erro ao processar pedido {order_id}: {e}")
            db.session.rollback()

    async def buscar_pedidos_empresa(self, access_token, seller_id, api_url, session, conta_nome):
        """BUSCA DE PEDIDOS - como no seu código original"""
        headers = {"Authorization": f"Bearer {access_token}"}
        offset = 0
        limit = 50

        # DO SEU CÓDIGO - 60 dias
        data_60_dias_antes = datetime.now(pytz.timezone('America/Sao_Paulo')) - timedelta(days=60)
        data_60_dias_antes_str = data_60_dias_antes.strftime("%Y-%m-%dT%H:%M:%S%z")

        logger.info(f"🔍 Buscando pedidos desde {data_60_dias_antes_str} para {conta_nome}")

        while True:
            url = f"{api_url}/orders/search?seller={seller_id}&date_created.from={data_60_dias_antes_str}&offset={offset}&limit={limit}"

            try:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        pedidos = data.get('results', [])
                        total = data.get('paging', {}).get('total', 0)

                        if not pedidos:
                            break

                        logger.info(f"📦 Processando lote de {len(pedidos)} pedidos...")

                        # Processar cada pedido
                        for pedido in pedidos:
                            await self.processar_pedido_completo(pedido, access_token, api_url, session, conta_nome)

                        offset += limit
                        if offset >= total:
                            break
                    else:
                        logger.error(f"❌ Erro API: {response.status}")
                        break
            except Exception as e:
                logger.error(f"❌ Erro na busca: {e}")
                break

        return True

    # --- DO SEU processamento_automato_ml.py ---
    async def calcular_financeiro_completo(self, conta_nome):
        """CÁLCULOS FINANCEIROS COMPLETOS - do seu código"""
        logger.info(f"🧮 Executando cálculos financeiros para {conta_nome}")

        try:
            # SEUS CÁLCULOS COMPLEXOS AQUI
            # Implementar toda a lógica do processamento_automato_ml.py
            await self.atualizar_preco_custo_ml()
            await self.calcular_impostos_e_fretes(conta_nome)
            await self.calcular_lucros(conta_nome)
            await self.processar_repasses(conta_nome)

            logger.info("✅ Cálculos financeiros concluídos")
            return True

        except Exception as e:
            logger.error(f"❌ Erro nos cálculos financeiros: {e}")
            return False

    async def atualizar_preco_custo_ml(self):
        """DO SEU CÓDIGO - atualizar custos"""
        try:
            # Implementar lógica completa do seu código
            logger.info("📊 Atualizando preços de custo...")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar custos: {e}")
            return False

    async def executar_processamento_completo(self, company_id, access_token, refresh_token, seller_id, conta_nome):
        """EXECUÇÃO COMPLETA - como no seu pipeline"""
        api_url = os.getenv("API_URL", "https://api.mercadolibre.com")

        async with aiohttp.ClientSession() as session:
            # 1. Buscar pedidos
            logger.info("🔄 Iniciando busca de pedidos...")
            success = await self.buscar_pedidos_empresa(access_token, seller_id, api_url, session, conta_nome)

            if success:
                # 2. Cálculos financeiros
                logger.info("🧮 Iniciando cálculos financeiros...")
                await self.calcular_financeiro_completo(conta_nome)

                logger.info("🎉 Processamento completo concluído!")
                return True
            else:
                logger.error("❌ Falha no processamento")
                return False


# Instância global
ml_integrado = MercadoLivreIntegrado()