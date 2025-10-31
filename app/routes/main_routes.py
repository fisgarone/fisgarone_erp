# app/routes/main_routes.py - VERSÃO FINAL DE PRODUÇÃO

from flask import Blueprint, render_template

# Cria o Blueprint para as rotas principais.
main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def dashboard():
    """
    Serve a página principal do dashboard.
    O Flask, configurado no __init__.py, irá procurar por 'index.html'
    na pasta 'frontend'.
    """
    # A linha que renderiza o arquivo HTML correto.
    return render_template('index.html')
