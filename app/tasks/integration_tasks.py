# app/tasks/integration_tasks.py
from app.extensions import db
from app.models.company_model import Company, IntegrationConfig
from app.services.integration_orchestrator import IntegrationOrchestrator
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def sincronizar_todas_empresas_automatico():
    """Tarefa automática principal - sincroniza TODAS as empresas ativas"""
    try:
        empresas_ativas = Company.query.filter_by(ativo=True).all()

        for empresa in empresas_ativas:
            try:
                # Verificar se tem integrações ativas
                config = IntegrationConfig.query.filter_by(company_id=empresa.id).first()

                if config and config.tem_integracao_ativa():
                    logger.info(f"Iniciando sincronização automática - Empresa: {empresa.nome_fantasia}")

                    orchestrator = IntegrationOrchestrator(empresa.id)

                    # Executar sincronizações automáticas
                    if config.sincronizar_pedidos_auto:
                        orchestrator.sincronizar_pedidos_automatico()

                    if config.sincronizar_produtos_auto:
                        orchestrator.sincronizar_produtos_automatico()

                    logger.info(f"Sincronização concluída - Empresa: {empresa.nome_fantasia}")

            except Exception as e:
                logger.error(f"Erro sincronização empresa {empresa.id}: {e}")
                continue  # Continua com as próximas empresas

        logger.info(f"Sincronização automática concluída para {len(empresas_ativas)} empresas")

    except Exception as e:
        logger.error(f"Erro geral sincronização automática: {e}")


def sincronizar_empresa_especifica(company_id):
    """Sincroniza uma empresa específica (para agendamento individual)"""
    try:
        empresa = Company.query.get(company_id)
        if not empresa or not empresa.ativo:
            return

        config = IntegrationConfig.query.filter_by(company_id=company_id).first()
        if not config or not config.tem_integracao_ativa():
            return

        logger.info(f"Sincronização individual - Empresa: {empresa.nome_fantasia}")

        orchestrator = IntegrationOrchestrator(company_id)

        if config.sincronizar_pedidos_auto:
            orchestrator.sincronizar_pedidos_automatico()

        if config.sincronizar_produtos_auto:
            orchestrator.sincronizar_produtos_automatico()

        logger.info(f"Sincronização individual concluída - Empresa: {empresa.nome_fantasia}")

    except Exception as e:
        logger.error(f"Erro sincronização individual {company_id}: {e}")


def verificar_tokens_automatico():
    """Verifica e renova tokens automaticamente (diariamente)"""
    try:
        configs = IntegrationConfig.query.filter(
            (IntegrationConfig.ml_ativo == True) | (IntegrationConfig.shopee_ativo == True)
        ).all()

        for config in configs:
            try:
                # Placeholder para lógica de refresh de tokens
                # Seus códigos de refresh serão inseridos aqui
                logger.info(f"Verificando tokens - Empresa: {config.company_id}")

            except Exception as e:
                logger.error(f"Erro verificar tokens empresa {config.company_id}: {e}")
                continue

        logger.info("Verificação de tokens automática concluída")

    except Exception as e:
        logger.error(f"Erro verificação tokens: {e}")