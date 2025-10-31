# setup_company.py - VERSÃO FINAL ALINHADA COM .ENV

import os
from app import create_app
from app.extensions import db
from app.models.company import Company, IntegrationConfig

app = create_app()
CONTAS = ["TOYS", "COMERCIAL", "PESCA", "CAMPING"]

with app.app_context():
    print("Iniciando setup multi-empresa alinhado com .env...")
    for conta_sufixo in CONTAS:
        cnpj = os.environ.get(f'CNPJ_{conta_sufixo}')
        if not cnpj:
            print(f"Dados para a conta {conta_sufixo} não encontrados. Pulando.")
            continue

        nome_fantasia = os.environ.get(f'NOME_FANTASIA_{conta_sufixo}')
        razao_social = os.environ.get(f'RAZAO_SOCIAL_{conta_sufixo}')
        ml_app_id = os.environ.get(f'CLIENT_ID_{conta_sufixo}')
        ml_client_secret = os.environ.get(f'CLIENT_SECRET_{conta_sufixo}')
        ml_access_token = os.environ.get(f'ACCESS_TOKEN_{conta_sufixo}')  # LENDO O ACCESS TOKEN
        ml_refresh_token = os.environ.get(f'REFRESH_TOKEN_{conta_sufixo}')
        ml_seller_id = os.environ.get(f'SELLER_ID_{conta_sufixo}')

        print(f"\n--- Processando {nome_fantasia} ({conta_sufixo}) ---")
        company = Company.query.filter_by(cnpj=cnpj).first()
        if not company:
            print(f"Criando nova empresa: {nome_fantasia}")
            company = Company(cnpj=cnpj, razao_social=razao_social, nome_fantasia=nome_fantasia, ativo=True)
            db.session.add(company)
            db.session.commit()

        integration = IntegrationConfig.query.filter_by(company_id=company.id).first()
        if not integration:
            print(f"Criando configuração de integração para {nome_fantasia}")
            integration = IntegrationConfig(company_id=company.id)
            db.session.add(integration)

        print(f"Atualizando credenciais ML para {nome_fantasia}")
        integration.ml_ativo = True
        integration.ml_app_id = ml_app_id
        integration.ml_client_secret = ml_client_secret
        integration.ml_access_token = ml_access_token  # SALVANDO O ACCESS TOKEN
        integration.ml_refresh_token = ml_refresh_token
        integration.ml_seller_id = ml_seller_id

        db.session.commit()
        print(f"✅ {nome_fantasia} configurada com sucesso.")
    print("\nSetup multi-empresa concluído.")
