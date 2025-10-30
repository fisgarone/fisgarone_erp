# app/tasks/company_tasks.py
from app.extensions import db
from app.models.company_model import Company
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def agendar_sincronizacao_inicial(company_id):
    """Agenda sincronização inicial quando empresa é criada/ativada"""
    try:
        from app.tasks.scheduler import agendar_tarefa_empresa

        # Agendar sincronização para daqui a 1 minuto
        agendar_tarefa_empresa(
            company_id,
            'sincronizacao_inicial',
            sincronizar_dados_iniciais,
            minutos=1
        )

        logger.info(f"Sincronização inicial agendada para empresa {company_id}")

    except Exception as e:
        logger.error(f"Erro ao agendar sincronização inicial: {e}")


def sincronizar_dados_iniciais(company_id):
    """Sincroniza dados iniciais automaticamente para nova empresa"""
    try:
        empresa = Company.query.get(company_id)
        if not empresa or not empresa.ativo:
            return

        logger.info(f"Iniciando sincronização inicial para {empresa.nome_fantasia}")

        # Aqui virão as sincronizações com ML, Shopee, etc
        # Por enquanto é um placeholder

        logger.info(f"Sincronização inicial concluída para {empresa.nome_fantasia}")

    except Exception as e:
        logger.error(f"Erro na sincronização inicial: {e}")


def verificar_empresas_inativas():
    """Tarefa automática para verificar e processar empresas inativas"""
    try:
        # Empresas inativas há mais de 30 dias
        limite = datetime.utcnow() - timedelta(days=30)
        empresas_inativas = Company.query.filter(
            Company.ativo == False,
            Company.data_atualizacao < limite
        ).all()

        for empresa in empresas_inativas:
            logger.info(f"Processando empresa inativa: {empresa.cnpj}")
            # Aqui pode-se fazer cleanup de dados, etc

    except Exception as e:
        logger.error(f"Erro ao verificar empresas inativas: {e}")