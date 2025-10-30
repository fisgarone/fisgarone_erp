# app/controllers/integration_controller.py
from flask import request, jsonify
from app.services.integration_orchestrator import IntegrationOrchestrator
from app.models.company import IntegrationConfig
from app.extensions import db
import logging

logger = logging.getLogger(__name__)


class IntegrationController:

    @staticmethod
    def configurar_integracao(company_id):
        """Configura integração automaticamente para uma empresa"""
        try:
            dados = request.get_json()
            config = IntegrationConfig.query.filter_by(company_id=company_id).first()

            if not config:
                return jsonify({'erro': 'Configuração não encontrada'}), 404

            # Configurar Mercado Livre
            if 'mercado_livre' in dados:
                ml_config = dados['mercado_livre']
                config.ml_ativo = ml_config.get('ativo', False)
                config.ml_app_id = ml_config.get('app_id')
                config.ml_client_secret = ml_config.get('client_secret')
                config.ml_access_token = ml_config.get('access_token')
                config.ml_refresh_token = ml_config.get('refresh_token')

            # Configurar Shopee
            if 'shopee' in dados:
                shopee_config = dados['shopee']
                config.shopee_ativo = shopee_config.get('ativo', False)
                config.shopee_partner_id = shopee_config.get('partner_id')
                config.shopee_secret_key = shopee_config.get('secret_key')
                config.shopee_access_token = shopee_config.get('access_token')

            # Configurações automáticas
            if 'automacao' in dados:
                auto_config = dados['automacao']
                config.sincronizar_pedidos_auto = auto_config.get('sincronizar_pedidos', True)
                config.sincronizar_produtos_auto = auto_config.get('sincronizar_produtos', True)
                config.sincronizar_estoque_auto = auto_config.get('sincronizar_estoque', True)

            db.session.commit()

            # Inicializar orquestrador com novas configurações
            orchestrator = IntegrationOrchestrator(company_id)
            status_conexoes = orchestrator.verificar_conexoes()

            return jsonify({
                'mensagem': 'Integração configurada com sucesso',
                'conexoes': status_conexoes
            }), 200

        except Exception as e:
            logger.error(f"Erro configurar integração: {e}")
            return jsonify({'erro': str(e)}), 500

    @staticmethod
    def sincronizar_agora(company_id):
        """Força sincronização manual (útil para testes)"""
        try:
            orchestrator = IntegrationOrchestrator(company_id)

            # Sincronizar tudo
            resultado_pedidos = orchestrator.sincronizar_pedidos_automatico()
            resultado_produtos = orchestrator.sincronizar_produtos_automatico()

            return jsonify({
                'mensagem': 'Sincronização executada',
                'pedidos': resultado_pedidos,
                'produtos': resultado_produtos
            }), 200

        except Exception as e:
            logger.error(f"Erro sincronização manual: {e}")
            return jsonify({'erro': str(e)}), 500

    @staticmethod
    def status_integracao(company_id):
        """Retorna status completo das integrações"""
        try:
            config = IntegrationConfig.query.filter_by(company_id=company_id).first()

            if not config:
                return jsonify({'erro': 'Configuração não encontrada'}), 404

            orchestrator = IntegrationOrchestrator(company_id)
            status_conexoes = orchestrator.verificar_conexoes()

            return jsonify({
                'company_id': company_id,
                'configuracoes': {
                    'mercado_livre': {
                        'ativo': config.ml_ativo,
                        'sincronizar_pedidos': config.sincronizar_pedidos_auto,
                        'sincronizar_produtos': config.sincronizar_produtos_auto
                    },
                    'shopee': {
                        'ativo': config.shopee_ativo,
                        'sincronizar_pedidos': config.sincronizar_pedidos_auto,
                        'sincronizar_produtos': config.sincronizar_produtos_auto
                    }
                },
                'conexoes': status_conexoes
            }), 200

        except Exception as e:
            logger.error(f"Erro status integração: {e}")
            return jsonify({'erro': str(e)}), 500


class IntegrationAutomationController:

    @staticmethod
    def executar_sincronizacao_auto(company_id):
        """Endpoint para ser chamado pelos agendadores automáticos"""
        try:
            orchestrator = IntegrationOrchestrator(company_id)

            # Executar sincronizações baseado nas configurações
            resultados = {}

            if orchestrator.config.sincronizar_pedidos_auto:
                resultados['pedidos'] = orchestrator.sincronizar_pedidos_automatico()

            if orchestrator.config.sincronizar_produtos_auto:
                resultados['produtos'] = orchestrator.sincronizar_produtos_automatico()

            logger.info(f"Sincronização automática executada - Empresa: {company_id}")
            return jsonify(resultados), 200

        except Exception as e:
            logger.error(f"Erro sincronização automática: {e}")
            return jsonify({'erro': str(e)}), 500