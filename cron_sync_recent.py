#!/usr/bin/env python3
"""
Script para Cron Job: Sincronização Recente (2 horas)
Executa a cada 3 minutos para capturar vendas em tempo real
"""

import sys
import os

# Adiciona o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.services.mercado_livre_service import sync_recent_orders

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        print("⚡ Iniciando sincronização recente (2 horas)...")
        sync_recent_orders()
        print("✅ Sincronização recente finalizada!")
