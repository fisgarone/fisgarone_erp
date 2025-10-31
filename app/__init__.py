# app/__init__.py - VERSÃO CORRIGIDA E INTEGRADA

from flask import Flask
from .extensions import db, migrate
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    # --- REGISTRO DE ROTAS (MÉTODO HÍBRIDO COMPATÍVEL) ---

    # 1. Registra as rotas de ML usando a sua função original
    from app.routes.ml_routes import init_ml_routes
    init_ml_routes(app)

    # 2. Registra os outros Blueprints existentes
    from app.routes.company_routes import company_bp
    from app.routes.integration_routes import integration_bp
    app.register_blueprint(company_bp, url_prefix='/api/companies')
    app.register_blueprint(integration_bp, url_prefix='/api/integration')

    # 3. Registra o novo Blueprint da página principal (Dashboard)
    from app.routes.main_routes import main_bp
    app.register_blueprint(main_bp, url_prefix='/')

    return app
