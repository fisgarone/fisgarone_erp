# app/__init__.py - VERSÃO FINAL COM INJEÇÃO DIRETA DE DB_URL

import os
from flask import Flask
from .extensions import db, migrate
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- INJEÇÃO DIRETA DA DATABASE_URL ---
    # 1. Lê a DATABASE_URL diretamente do ambiente de execução.
    db_url = os.environ.get('DATABASE_URL')

    # 2. Força a configuração do SQLAlchemy a usar esta URL.
    #    Isso garante que o Web Service e o Shell usem a mesma conexão.
    if db_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://", 1)
    else:
        # Fallback para um banco de dados local se a variável não for encontrada
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dev.db'
        print("AVISO: DATABASE_URL não encontrada, usando dev.db local.")

    # O resto da inicialização permanece o mesmo
    db.init_app(app)
    migrate.init_app(app, db)

    # --- REGISTRO DE BLUEPRINTS ---
    # (Esta parte do seu código permanece como está)
    from .routes.main_routes import main_bp
    from .routes.ml_routes import ml_bp
    # ... etc

    app.register_blueprint(main_bp, url_prefix='/')
    app.register_blueprint(ml_bp, url_prefix='/api/ml')
    # ... etc

    return app
