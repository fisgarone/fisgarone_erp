# wsgi.py
# Ponto de entrada para o servidor Gunicorn na Render.

from app import create_app

# O Gunicorn irá procurar por esta variável 'app' por padrão.
app = create_app()
