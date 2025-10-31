# app/__init__.py - VERSÃO COM CAMINHOS ABSOLUTOS (CORRETA)
import os
from flask import Flask
from .extensions import db, migrate
from config import Config

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
FRONTEND_FOLDER = os.path.join(BASE_DIR, 'frontend')

def create_app(config_class=Config):
    app = Flask(__name__, template_folder=FRONTEND_FOLDER, static_folder=FRONTEND_FOLDER)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)

    from .routes.main_routes import main_bp
    from .routes.ml_routes import ml_bp
    from .routes.company_routes import company_bp
    from .routes.integration_routes import integration_bp

    app.register_blueprint(main_bp, url_prefix='/')
    app.register_blueprint(ml_bp, url_prefix='/api/ml')
    app.register_blueprint(company_bp, url_prefix='/api/companies')
    app.register_blueprint(integration_bp, url_prefix='/api/integration')

    return app
