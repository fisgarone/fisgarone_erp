# config.py - VERSÃO RENDER (PostgreSQL)
import os
from datetime import timedelta
from dotenv import load_dotenv

# Carrega variáveis de ambiente de um arquivo .env (para desenvolvimento local)
load_dotenv()

class Config:
    """Configurações da aplicação."""

    # Chave secreta para segurança da sessão e outras funcionalidades
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a-hard-to-guess-string')

    # Configuração do Banco de Dados
    # A Render injeta a URL do banco de dados na variável de ambiente DATABASE_URL.
    # Esta linha lê essa variável. Se não for encontrada (em ambiente local),
    # ela usa um banco de dados SQLite local como fallback.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # O SQLAlchemy >= 2.0 emite um aviso se a URL do Postgres não for 'postgresql'.
    # Esta lógica corrige isso automaticamente para a Render.
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            "postgres://", "postgresql://", 1
        )

    # Desativa uma funcionalidade do Flask-SQLAlchemy que não é necessária e consome recursos.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configurações recomendadas para o pool de conexões em produção.
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True
    }

    # Configurações para JWT (se aplicável)
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'another-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

