# app/services/integration_orchestrator.py
from app.services.mercado_livre_service import MercadoLivreService
from app.services.shopee_service import ShopeeService
from app.services.mercado_livre_service import MercadoLivreService
from app.models.company import IntegrationConfig
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class IntegrationOrchestrator:
    """Orquestrador de integrações automáticas"""

    def __init__(self, company_id):
        self.company_id = company_id
        self.config = IntegrationConfig.query.filter_by(company_id=company_id).first()
        self.services = {}

        self._inicializar_servicos()

    def _inicializar_servicos(self):
        """Inicializa serviços baseado nas configurações"""
        if self.config and self.config.ml_ativo and self.config.ml_access_token:
            self.services['mercado_livre'] = MercadoLivreService(
                access_token=self.config.ml_access_token,
                refresh_token=self.config.ml_refresh_token
            )

        if self.config and self.config.shopee_ativo and self.config.shopee_access_token:
            self.services['shopee'] = ShopeeService(
                partner_id=self.config.shopee_partner_id,
                secret_key=self.config.shopee_secret_key,
                access_token=self.config.shopee_access_token
            )

    def sincronizar_pedidos_automatico(self):
        """Sincroniza pedidos de todas as plataformas automaticamente"""
        resultados = {
            'total_pedidos': 0,
            'plataformas': {},
            'timestamp': datetime.utcnow().isoformat()
        }

        try:
            # Mercado Livre
            if 'mercado_livre' in self.services and self.config.sincronizar_pedidos_auto:
                pedidos_ml = self.services['mercado_livre'].obter_pedidos_automatico()
                resultados['plataformas']['mercado_livre'] = {
                    'pedidos': len(pedidos_ml),
                    'status': 'sucesso'
                }
                resultados['total_pedidos'] += len(pedidos_ml)

            # Shopee
            if 'shopee' in self.services and self.config.sincronizar_pedidos_auto:
                pedidos_shopee = self.services['shopee'].obter_pedidos_automatico()
                resultados['plataformas']['shopee'] = {
                    'pedidos': len(pedidos_shopee),
                    'status': 'sucesso'
                }
                resultados['total_pedidos'] += len(pedidos_shopee)

            logger.info(f"✅ Sincronização automática concluída - {resultados['total_pedidos']} pedidos")
            return resultados

        except Exception as e:
            logger.error(f"❌ Erro na sincronização automática: {e}")
            resultados['erro'] = str(e)
            return resultados

    def sincronizar_produtos_automatico(self):
        """Sincroniza produtos de todas as plataformas automaticamente"""
        resultados = {
            'total_produtos': 0,
            'plataformas': {},
            'timestamp': datetime.utcnow().isoformat()
        }

        try:
            # Mercado Livre
            if 'mercado_livre' in self.services and self.config.sincronizar_produtos_auto:
                produtos_ml = self.services['mercado_livre'].obter_produtos_automatico()
                resultados['plataformas']['mercado_livre'] = {
                    'produtos': len(produtos_ml),
                    'status': 'sucesso'
                }
                resultados['total_produtos'] += len(produtos_ml)

            # Shopee
            if 'shopee' in self.services and self.config.sincronizar_produtos_auto:
                produtos_shopee = self.services['shopee'].obter_produtos_automatico()
                resultados['plataformas']['shopee'] = {
                    'produtos': len(produtos_shopee),
                    'status': 'sucesso'
                }
                resultados['total_produtos'] += len(produtos_shopee)

            logger.info(f"✅ Sincronização produtos concluída - {resultados['total_produtos']} produtos")
            return resultados

        except Exception as e:
            logger.error(f"❌ Erro na sincronização de produtos: {e}")
            resultados['erro'] = str(e)
            return resultados

    def verificar_conexoes(self):
        """Verifica conexão com todas as plataformas automaticamente"""
        status = {}

        for plataforma, servico in self.services.items():
            try:
                if plataforma == 'mercado_livre':
                    servico.obter_vendedor_id()
                    status[plataforma] = {'conectado': True, 'erro': None}

                elif plataforma == 'shopee':
                    servico.obter_produtos_automatico(limite=1)
                    status[plataforma] = {'conectado': True, 'erro': None}

            except Exception as e:
                status[plataforma] = {'conectado': False, 'erro': str(e)}

        return status