#!/usr/bin/env python3
"""
Script para Cron Job: Sincronização Completa (60 dias)
Executa a cada 3 horas para manter dados atualizados
"""

import sys
import os

# Adiciona o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.services.mercado_livre_service import sync_full_reconciliation

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        print("🔄 Iniciando sincronização completa (60 dias)...")
        sync_full_reconciliation()
        print("✅ Sincronização completa finalizada!")
