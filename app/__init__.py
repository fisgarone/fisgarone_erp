# app/__init__.py
import os
from flask import Flask
from .extensions import db, migrate

# Blueprints
from app.routes.main_routes import main_bp
from app.routes.ml_routes import init_ml_routes
from app.routes.company_routes import company_bp
from app.routes.integration_routes import integration_bp
from app.routes.filter_routes import bp as filters_bp

def create_app():
    # Base do projeto para static/templates
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    app = Flask(
        __name__,
        static_folder=os.path.join(project_root, 'frontend'),
        static_url_path='',
        template_folder=os.path.join(project_root, 'frontend')
    )

    # Configurações
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Extensões
    db.init_app(app)
    migrate.init_app(app, db)

    # Registrar blueprints (uma vez cada)
    app.register_blueprint(filters_bp)                              # /api/filters/accounts
    app.register_blueprint(main_bp)                                 # frontend/dashboard
    init_ml_routes(app)                                             # rotas ML
    app.register_blueprint(company_bp, url_prefix='/api/companies')
    app.register_blueprint(integration_bp, url_prefix='/api/integration')

    print("✅ Aplicação criada e rotas registradas com sucesso!")
    return app
