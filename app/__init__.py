# app/__init__.py - VERSÃO CORRIGIDA E VALIDADA
from flask import Flask
from .extensions import db, migrate
import os

# Importar Blueprints
from app.routes.main_routes import main_bp
from app.routes.ml_routes import init_ml_routes
from app.routes.company_routes import company_bp
from app.routes.integration_routes import integration_bp

def create_app():
    # Usar o nome do diretório do projeto como base para os caminhos
    # Isso garante que o Flask encontre a pasta `frontend` corretamente
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    app = Flask(__name__,
                # Caminho para os arquivos estáticos (CSS, JS, imagens)
                static_folder=os.path.join(project_root, 'frontend'),
                static_url_path='',
                # Caminho para os templates HTML
                template_folder=os.path.join(project_root, 'frontend'))

    # Carregar configurações do ambiente (DATABASE_URL)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)

    # === REGISTRAR BLUEPRINTS ===
    # 1. Rotas principais (frontend e dashboard)
    app.register_blueprint(main_bp)

    # 2. Rotas da API do Mercado Livre
    init_ml_routes(app)

    # 3. Outras rotas da API
    app.register_blueprint(company_bp, url_prefix='/api/companies')
    app.register_blueprint(integration_bp, url_prefix='/api/integration')

    print("✅ Aplicação criada e rotas registradas com sucesso!")

    return app