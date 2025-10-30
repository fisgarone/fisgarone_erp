# app/tasks/scheduler.py (ATUALIZAR)
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
scheduler = None


def iniciar_agendadores(app):
    """Inicializa os agendadores automáticos"""
    global scheduler

    if scheduler and scheduler.running:
        logger.info("Agendadores já estão rodando")
        return

    try:
        scheduler = BackgroundScheduler()
        scheduler.start()

        # AGENDAR TAREFAS DE INTEGRAÇÃO AUTOMÁTICA
        from app.tasks.integration_tasks import (
            sincronizar_todas_empresas_automatico,
            verificar_tokens_automatico
        )

        # Sincronização geral a cada 30 minutos
        scheduler.add_job(
            sincronizar_todas_empresas_automatico,
            'interval',
            minutes=30,
            id='sincronizacao_geral_automatica'
        )

        # Verificação de tokens uma vez por dia
        scheduler.add_job(
            verificar_tokens_automatico,
            'interval',
            days=1,
            id='verificacao_tokens_automatica'
        )

        logger.info("✅ Agendadores de integração automáticos iniciados")

    except Exception as e:
        logger.error(f"Erro ao iniciar agendadores: {e}")


def agendar_tarefa_empresa(company_id, nome_tarefa, funcao, minutos=30):
    """Agenda uma tarefa específica para uma empresa"""
    global scheduler

    if not scheduler:
        logger.error("Scheduler não inicializado")
        return

    try:
        job_id = f"empresa_{company_id}_{nome_tarefa}"

        # Remove job existente se houver
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)

        # Agenda nova tarefa
        scheduler.add_job(
            funcao,
            'interval',
            minutes=minutos,
            args=[company_id],
            id=job_id
        )

        logger.info(f"Tarefa {nome_tarefa} agendada para empresa {company_id}")

    except Exception as e:
        logger.error(f"Erro ao agendar tarefa: {e}")


def reagendar_tarefas_empresa(company_id):
    """Reagenda todas as tarefas de uma empresa baseado nas configurações"""
    try:
        from app.models.company_model import CompanyConfig

        config = CompanyConfig.query.filter_by(company_id=company_id).first()
        if not config:
            return

        # Aqui você pode reagendar tarefas baseado nas configurações
        if config.auto_sincronizar_estoque:
            from app.tasks.integration_tasks import sincronizar_estoque_empresa
            agendar_tarefa_empresa(
                company_id,
                'sincronizar_estoque',
                sincronizar_estoque_empresa,
                minutos=config.intervalo_sincronizacao
            )

        logger.info(f"Tarefas reagendadas para empresa {company_id}")

    except Exception as e:
        logger.error(f"Erro ao reagendar tarefas: {e}")


def obter_status_tarefas_empresa(company_id):
    """Retorna status das tarefas agendadas para uma empresa"""
    global scheduler

    if not scheduler:
        return {'erro': 'Scheduler não inicializado'}

    try:
        jobs = scheduler.get_jobs()
        empresa_jobs = [job for job in jobs if f"empresa_{company_id}_" in job.id]

        status = {
            'total_tarefas': len(empresa_jobs),
            'tarefas_ativas': [],
            'proxima_execucao': None
        }

        for job in empresa_jobs:
            status['tarefas_ativas'].append({
                'id': job.id,
                'proxima_execucao': job.next_run_time.isoformat() if job.next_run_time else None
            })

        return status

    except Exception as e:
        logger.error(f"Erro ao obter status tarefas: {e}")
        return {'erro': str(e)}