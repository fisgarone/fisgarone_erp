# manage.py

from flask.cli import FlaskGroup
from app import create_app
from app.extensions import db
from app.models import user  # importa os modelos

app = create_app()
cli = FlaskGroup(app)

if __name__ == "__main__":
    cli()
