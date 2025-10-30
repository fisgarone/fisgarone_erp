# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

# Inicializar extensões
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()

# Remover socketio se não está sendo usado
# Se precisar de WebSockets depois, adicionamos