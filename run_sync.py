# run_sync.py - VERSÃO CORRIGIDA COM CONTEXTO DA APLICAÇÃO
import sys
from app import create_app
from app.services.mercado_livre_service import sync_full_reconciliation, sync_recent_orders

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python run_sync.py [full|recent]")
        sys.exit(1)

    mode = sys.argv[1]

    # CORREÇÃO: Criar o contexto da aplicação Flask
    app = create_app()

    with app.app_context():
        if mode == 'full':
            sync_full_reconciliation()
        elif mode == 'recent':
            sync_recent_orders()
        else:
            print(f"Modo desconhecido: {mode}. Use 'full' ou 'recent'.")
            sys.exit(1)