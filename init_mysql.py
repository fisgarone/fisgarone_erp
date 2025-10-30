# init_mysql.py
import sys
import os
import logging
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def init_mysql():
    logger.info("🚀 INICIALIZAÇÃO MYSQL HOSTINGER")

    try:
        from flask import Flask
        from app.extensions import db
        from config import Config

        # Criar app
        app = Flask(__name__)
        app.config.from_object(Config)
        db.init_app(app)

        with app.app_context():
            logger.info("🗃️ Conectando ao MySQL Hostinger...")

            # Testar conexão
            result = db.session.execute(text('SELECT version()'))
            version = result.scalar()
            logger.info(f"🔗 MySQL: {version}")

            # Importar modelos
            from app.models.company import Company, CompanyConfig, IntegrationConfig
            from app.models.ml_models import VendaML, RepasseML, CustoML
            from app.models.user import User

            logger.info("📦 Criando tabelas...")
            db.create_all()
            logger.info("✅ Tabelas criadas!")

            # Listar tabelas (MySQL)
            result = db.session.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result]
            logger.info("📊 Tabelas no MySQL:")
            for table in tables:
                logger.info(f"   - {table}")

            # Verificar/Criar empresa
            existing = Company.query.first()
            if existing:
                logger.info(f"✅ Empresa existente: {existing.nome_fantasia} (ID: {existing.id})")
                company_id = existing.id
            else:
                company = Company(
                    cnpj='12.345.678/0001-90',
                    razao_social='Empresa Teste LTDA',
                    nome_fantasia='Teste ML MySQL'
                )
                db.session.add(company)
                db.session.flush()
                company_id = company.id

                # Configurar ML
                ml_config = IntegrationConfig(
                    company_id=company.id,
                    platform='mercado_livre',
                    client_id=os.getenv('CLIENT_ID_TOYS'),
                    client_secret=os.getenv('CLIENT_SECRET_TOYS'),
                    access_token=os.getenv('ACCESS_TOKEN_TOYS'),
                    refresh_token=os.getenv('REFRESH_TOKEN_TOYS'),
                    seller_id=os.getenv('SELLER_ID_TOYS'),
                    is_active=True
                )
                db.session.add(ml_config)
                db.session.commit()

                logger.info(f"✅ Nova empresa criada: {company.nome_fantasia} (ID: {company.id})")

            logger.info("🎉 MYSQL HOSTINGER CONFIGURADO COM SUCESSO!")
            return company_id

    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    company_id = init_mysql()
    if company_id:
        print(f"\n🎯 MYSQL PRONTO! Empresa ID: {company_id}")
        print("👉 Agora execute: python run.py")
    else:
        print("\n💥 FALHA - Verifique os logs acima")