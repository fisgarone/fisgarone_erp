# app/__init__.py - VERSÃO ORIGINAL
from flask import Flask
from .extensions import db, migrate
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)

    # Registrar rotas NA FORMA ORIGINAL
    from app.routes.ml_routes import init_ml_routes
    from app.routes.company_routes import company_bp
    from app.routes.integration_routes import integration_bp

    init_ml_routes(app)  # ✅ FORMA ORIGINAL
    app.register_blueprint(company_bp, url_prefix='/api/companies')
    app.register_blueprint(integration_bp, url_prefix='/api/integration')

    return app