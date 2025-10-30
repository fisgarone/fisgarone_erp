# ver_tabela.py
from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    result = db.session.execute(text("SHOW COLUMNS FROM vendas_ml"))
    print("📊 COLUNAS DA TABELA VENDAS_ML:")
    for col in result:
        print(f"  {col[0]}")