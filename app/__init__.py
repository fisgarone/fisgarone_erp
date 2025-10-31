# app/__init__.py - VERSÃO FINAL COM CONEXÃO FORÇADA

import os
from flask import Flask
from .extensions import db, migrate
from config import Config

# Caminhos para o frontend (mantém a tela funcionando)
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
FRONTEND_FOLDER = os.path.join(BASE_DIR, 'frontend')


def create_app(config_class=Config):
    app = Flask(__name__, template_folder=FRONTEND_FOLDER, static_folder=FRONTEND_FOLDER)
    app.config.from_object(config_class)

    # --- FORÇAR A CONEXÃO COM O BANCO DE DADOS DE PRODUÇÃO ---
    # Esta linha garante que a aplicação web use o banco de dados correto, sem exceção.
    app.config[
        'SQLALCHEMY_DATABASE_URI'] = 'postgresql://fisgarone_user:tNlFW2UjcqRnzw7gkqaxVq7a0KZH9lGC@dpg-d41s0i3e5dus73cocpd0-a/fisgarone_db_data'

    # Desativa um aviso desnecessário do SQLAlchemy
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # O resto da inicialização
    db.init_app(app)
    migrate.init_app(app, db)

    # Registro dos Blueprints
    from .routes.main_routes import main_bp
    from .routes.ml_routes import ml_bp
    from .routes.company_routes import company_bp
    from .routes.integration_routes import integration_bp

    app.register_blueprint(main_bp, url_prefix='/')
    app.register_blueprint(ml_bp, url_prefix='/api/ml')
    app.register_blueprint(company_bp, url_prefix='/api/companies')
    app.register_blueprint(integration_bp, url_prefix='/api/integration')

    return app
