# cron_sync_recent.py
from app import create_app
from app.services.integration_orchestrator import run_recent

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        # provider pode ser "ALL", "ML" ou "SHOPEE"
        # se quiser limitar contas: accounts=["TOYS","COMERCIAL","PESCA","CAMPING"]
        ok, fail = run_recent(provider="ALL")
        print(f"Resumo: OK={ok}  FAIL={fail}")
