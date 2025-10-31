# app/__init__.py - VERSÃO FINAL COM CAMINHOS ABSOLUTOS

import os
from flask import Flask
from .extensions import db, migrate
from config import Config

# --- CONFIGURAÇÃO DE CAMINHOS ABSOLUTOS ---
# 1. Encontra o caminho absoluto para o diretório raiz do projeto
#    No ambiente da Render, isso será algo como /opt/render/project/src
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# 2. Constrói o caminho absoluto para a pasta 'frontend'
FRONTEND_FOLDER = os.path.join(BASE_DIR, 'frontend')


def create_app(config_class=Config):
    # 3. Informa ao Flask para usar os caminhos absolutos
    app = Flask(
        __name__,
        template_folder=FRONTEND_FOLDER,
        static_folder=FRONTEND_FOLDER
    )

    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    # --- REGISTRO DE BLUEPRINTS (Inalterado) ---
    from .routes.main_routes import main_bp
    from .routes.ml_routes import ml_bp
    from .routes.company_routes import company_bp
    from .routes.integration_routes import integration_bp

    app.register_blueprint(main_bp, url_prefix='/')
    app.register_blueprint(ml_bp, url_prefix='/api/ml')
    app.register_blueprint(company_bp, url_prefix='/api/companies')
    app.register_blueprint(integration_bp, url_prefix='/api/integration')

    return app
