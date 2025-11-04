# app/services/shopee_service.py
import requests
import hashlib
import time
import logging
from datetime import datetime
from app.extensions import db

logger = logging.getLogger(__name__)


class ShopeeService:
    def __init__(self, partner_id, secret_key, access_token=None):
        self.base_url = "https://partner.shopeemobile.com"
        self.partner_id = partner_id
        self.secret_key = secret_key
        self.access_token = access_token
        self.session = requests.Session()

    def _gerar_assinatura(self, path, params=None):
        """Gera assinatura para autenticação Shopee"""
        timestamp = int(time.time())
        base_string = f"{self.partner_id}{path}{timestamp}"

        if params:
            # Ordenar parâmetros alfabeticamente
            sorted_params = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
            base_string += sorted_params

        base_string += self.secret_key
        return hashlib.sha256(base_string.encode()).hexdigest(), timestamp

    def get_headers(self):
        """Headers para requisições Shopee"""
        return {
            'Content-Type': 'application/json'
        }

    def obter_pedidos_automatico(self, data_inicio=None, limite=100):
        """Obtém pedidos automaticamente - para tarefas agendadas"""
        try:
            path = "/api/v2/order/get_order_list"
            params = {
                'page_size': min(limite, 100),
                'order_status': 'READY_TO_SHIP,PROCESSED,SHIPPED,COMPLETED'
            }

            if data_inicio:
                # Converter data para timestamp
                if isinstance(data_inicio, str):
                    data_inicio = datetime.fromisoformat(data_inicio.replace('Z', '+00:00'))
                params['time_range_field'] = 'create_time'
                params['time_from'] = int(data_inicio.timestamp())
                params['time_to'] = int(time.time())

            assinatura, timestamp = self._gerar_assinatura(path, params)

            url = f"{self.base_url}{path}"
            full_params = {
                'partner_id': self.partner_id,
                'timestamp': timestamp,
                'sign': assinatura,
                **params
            }

            if self.access_token:
                full_params['access_token'] = self.access_token

            response = self.session.get(url, headers=self.get_headers(), params=full_params)
            response.raise_for_status()

            dados = response.json()
            pedidos = dados.get('response', {}).get('order_list', [])

            logger.info(f"✅ {len(pedidos)} pedidos obtidos da Shopee")
            return pedidos

        except Exception as e:
            logger.error(f"❌ Erro ao obter pedidos Shopee: {e}")
            return []

    def obter_detalhes_pedido(self, order_sn):
        """Obtém detalhes de um pedido específico"""
        try:
            path = "/api/v2/order/get_order_detail"
            params = {
                'order_sn_list': order_sn
            }

            assinatura, timestamp = self._gerar_assinatura(path, params)

            url = f"{self.base_url}{path}"
            full_params = {
                'partner_id': self.partner_id,
                'timestamp': timestamp,
                'sign': assinatura,
                **params
            }

            if self.access_token:
                full_params['access_token'] = self.access_token

            response = self.session.get(url, headers=self.get_headers(), params=full_params)
            response.raise_for_status()

            return response.json().get('response', {}).get('order_list', [])

        except Exception as e:
            logger.error(f"Erro ao obter detalhes pedido {order_sn}: {e}")
            return []

    def obter_produtos_automatico(self, limite=100):
        """Obtém produtos automaticamente - para sincronização"""
        try:
            path = "/api/v2/product/get_item_list"
            params = {
                'page_size': min(limite, 100),
                'item_status': 'NORMAL'
            }

            assinatura, timestamp = self._gerar_assinatura(path, params)

            url = f"{self.base_url}{path}"
            full_params = {
                'partner_id': self.partner_id,
                'timestamp': timestamp,
                'sign': assinatura,
                **params
            }

            if self.access_token:
                full_params['access_token'] = self.access_token

            response = self.session.get(url, headers=self.get_headers(), params=full_params)
            response.raise_for_status()

            dados = response.json()
            produtos = dados.get('response', {}).get('item', [])

            logger.info(f"✅ {len(produtos)} produtos obtidos da Shopee")
            return produtos

        except Exception as e:
            logger.error(f"❌ Erro ao obter produtos Shopee: {e}")
            return []

    def obter_detalhes_produto(self, item_id):
        """Obtém detalhes de um produto específico"""
        try:
            path = "/api/v2/product/get_item_base_info"
            params = {
                'item_id_list': str(item_id)
            }

            assinatura, timestamp = self._gerar_assinatura(path, params)

            url = f"{self.base_url}{path}"
            full_params = {
                'partner_id': self.partner_id,
                'timestamp': timestamp,
                'sign': assinatura,
                **params
            }

            if self.access_token:
                full_params['access_token'] = self.access_token

            response = self.session.get(url, headers=self.get_headers(), params=full_params)
            response.raise_for_status()

            dados = response.json()
            return dados.get('response', {}).get('item_list', [])

        except Exception as e:
            logger.error(f"Erro ao obter produto {item_id}: {e}")
            return []

    def atualizar_estoque_automatico(self, produtos_locais):
        """Atualiza estoque automaticamente na Shopee"""
        try:
            for produto in produtos_locais:
                if produto.sku_shopee:
                    self.atualizar_estoque_shopee(
                        produto.sku_shopee,
                        produto.estoque_atual
                    )

            logger.info("✅ Estoque sincronizado com Shopee")
        except Exception as e:
            logger.error(f"❌ Erro sincronizar estoque Shopee: {e}")

    def atualizar_estoque_shopee(self, item_id, estoque):
        """Atualiza estoque de um produto na Shopee"""
        try:
            path = "/api/v2/product/update_stock"

            params = {
                'item_id': int(item_id),
                'stock_list': [
                    {
                        'model_id': 0,  # Modelo principal
                        'normal_stock': estoque
                    }
                ]
            }

            assinatura, timestamp = self._gerar_assinatura(path, params)

            url = f"{self.base_url}{path}"
            full_params = {
                'partner_id': self.partner_id,
                'timestamp': timestamp,
                'sign': assinatura,
                **params
            }

            if self.access_token:
                full_params['access_token'] = self.access_token

            response = self.session.post(url, headers=self.get_headers(), json=full_params)
            response.raise_for_status()

            return True

        except Exception as e:
            logger.error(f"Erro atualizar estoque item {item_id}: {e}")
            return False

# ====== Compatibilidade para o orquestrador (NÃO REMOVER) ======
# Alguns lugares importam estes nomes antigos. Estes "atalhos" redirecionam
# para as funções que você já tiver implementado (sync_full, run_full, etc).

def _call_existing(candidates, *args, **kwargs):
    import sys
    m = sys.modules[__name__]
    for name in candidates:
        if hasattr(m, name):
            return getattr(m, name)(*args, **kwargs)
    raise NotImplementedError(f"Nenhuma função encontrada entre: {candidates}")

def sync_full_reconciliation(*args, **kwargs):
    # tente na ordem; ajuste/adicione aqui se seu arquivo usar outro nome
    return _call_existing(
        ["sync_full_reconciliation", "sync_full", "run_full", "full_sync"],
        *args, **kwargs
    )

def sync_recent_orders(*args, **kwargs):
    # tente na ordem; ajuste/adicione aqui se seu arquivo usar outro nome
    return _call_existing(
        ["sync_recent_orders", "sync_recent", "run_recent", "recent_sync"],
        *args, **kwargs
    )
# ====== Fim da compatibilidade ======
