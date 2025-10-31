# app/routes/main_routes.py - VERSÃO FINAL COM BLUEPRINT DE FRONTEND DEDICADO

import os
from flask import Blueprint, render_template

# --- CONFIGURAÇÃO DE CAMINHOS ABSOLUTOS PARA ESTE BLUEPRINT ---
# Encontra o caminho absoluto para o diretório raiz do projeto
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
# Constrói o caminho absoluto para a pasta 'frontend'
FRONTEND_FOLDER = os.path.join(BASE_DIR, 'frontend')

# --- CRIAÇÃO DO BLUEPRINT DE FRONTEND ---
# Informa a este Blueprint específico onde encontrar seus templates e arquivos estáticos.
main_bp = Blueprint(
    'main_bp',
    __name__,
    template_folder=FRONTEND_FOLDER,
    static_folder=FRONTEND_FOLDER
)

@main_bp.route('/')
def dashboard():
    """
    Serve a página principal do dashboard.
    O Flask agora sabe que deve procurar 'dashboard.html' dentro de FRONTEND_FOLDER.
    """
    return render_template('dashboard.html')
