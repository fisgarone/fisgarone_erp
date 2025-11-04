# cron_sync_full.py
from app import create_app
from app.services.integration_orchestrator import run_full

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        # provider pode ser "ALL", "ML" ou "SHOPEE"
        # se quiser limitar contas: accounts=["TOYS","COMERCIAL","PESCA","CAMPING"]
        ok, fail = run_full(provider="ALL")
        print(f"Resumo: OK={ok}  FAIL={fail}")
