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
            # Sincroniza os últimos 60 dias para todas as empresas
            sync_full_reconciliation()
        elif mode == 'recent':
            # Sincroniza as últimas 3 horas (parâmetro padrão)
            sync_recent_orders()
        elif mode == 'recent3h':
            # Alias explícito para sincronizar as últimas 3 horas
            sync_recent_orders(hours_back=3)
        elif mode == 'last5m':
            # Sincroniza as vendas dos últimos 5 minutos
            # Ideal para atualizações quase em tempo real
            from app.services.mercado_livre_service import sync_last_five_minutes
            sync_last_five_minutes(minutes_back=5)
        else:
            print(f"Modo desconhecido: {mode}. Use 'full', 'recent', 'recent3h' ou 'last5m'.")
            sys.exit(1)