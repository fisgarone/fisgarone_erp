# app/__init__.py - VERSÃO PADRÃO E LIMPA

from flask import Flask
from .extensions import db, migrate
from config import Config


def create_app(config_class=Config):
    # Cria a aplicação Flask da forma padrão, sem configurar pastas de template globais.
    app = Flask(__name__)

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
