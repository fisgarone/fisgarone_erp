# app/routes/main_routes.py - VERSÃO DE DIAGNÓSTICO FORENSE

import os
from flask import Blueprint, jsonify

# Constrói o caminho absoluto para a pasta 'frontend'
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
FRONTEND_FOLDER = os.path.join(BASE_DIR, 'frontend')

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def diagnose_filesystem():
    """
    Rota de diagnóstico para listar o conteúdo da pasta do projeto e da pasta frontend.
    """
    try:
        # Lista o conteúdo da raiz do projeto (onde 'frontend' deveria estar)
        project_root_content = os.listdir(BASE_DIR)
    except Exception as e:
        project_root_content = [f"Erro ao listar raiz do projeto: {str(e)}"]

    try:
        # Tenta listar o conteúdo da pasta 'frontend'
        frontend_content = os.listdir(FRONTEND_FOLDER)
    except FileNotFoundError:
        frontend_content = ["ERRO: A pasta 'frontend' NÃO FOI ENCONTRADA neste caminho."]
    except Exception as e:
        frontend_content = [f"Erro ao listar pasta frontend: {str(e)}"]

    # Retorna a lista de arquivos como uma resposta JSON
    return jsonify({
        'DIAGNOSTICO_DO_SISTEMA_DE_ARQUIVOS': 'ATIVO',
        'CAMINHO_RAIZ_DO_PROJETO_ESPERADO': BASE_DIR,
        'CONTEUDO_DA_RAIZ_DO_PROJETO': project_root_content,
        'CAMINHO_DA_PASTA_FRONTEND_ESPERADO': FRONTEND_FOLDER,
        'CONTEUDO_DA_PASTA_FRONTEND': frontend_content
    })
