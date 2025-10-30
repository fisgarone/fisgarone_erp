# setup_company.py - VERSÃO MULTI-EMPRESA
import os
from app import create_app
from app.extensions import db
from app.models.company import Company, IntegrationConfig

app = create_app()

with app.app_context():
    print("Iniciando setup multi-empresa...")

    # Loop de 1 a 4 (ou mais, se necessário) para encontrar as variáveis de ambiente
    for i in range(1, 5):
        cnpj = os.environ.get(f'EMPRESA{i}_CNPJ')

        # Se não encontrar o CNPJ da empresa 'i', para o loop
        if not cnpj:
            print(f"Nenhuma variável de ambiente encontrada para EMPRESA{i}. Finalizando.")
            break

        nome_fantasia = os.environ.get(f'EMPRESA{i}_NOME_FANTASIA')
        razao_social = os.environ.get(f'EMPRESA{i}_RAZAO_SOCIAL')
        ml_app_id = os.environ.get(f'EMPRESA{i}_ML_APP_ID')
        ml_client_secret = os.environ.get(f'EMPRESA{i}_ML_CLIENT_SECRET')
        ml_refresh_token = os.environ.get(f'EMPRESA{i}_ML_REFRESH_TOKEN')

        print(f"\n--- Processando {nome_fantasia} ---")

        # Busca ou cria a empresa
        company = Company.query.filter_by(cnpj=cnpj).first()
        if not company:
            print(f"Criando nova empresa: {nome_fantasia}")
            company = Company(
                cnpj=cnpj,
                razao_social=razao_social,
                nome_fantasia=nome_fantasia,
                ativo=True
            )
            db.session.add(company)
            db.session.commit()
        else:
            print(f"Empresa {nome_fantasia} já existe. Atualizando...")
            company.razao_social = razao_social
            company.nome_fantasia = nome_fantasia
            company.ativo = True

        # Busca ou cria a configuração de integração
        integration = IntegrationConfig.query.filter_by(company_id=company.id).first()
        if not integration:
            print(f"Criando configuração de integração para {nome_fantasia}")
            integration = IntegrationConfig(company_id=company.id)
            db.session.add(integration)

        print(f"Atualizando credenciais ML para {nome_fantasia}")
        integration.ml_ativo = True
        integration.ml_app_id = ml_app_id
        integration.ml_client_secret = ml_client_secret
        integration.ml_refresh_token = ml_refresh_token

        db.session.commit()
        print(f"✅ {nome_fantasia} configurada com sucesso.")

    print("\nSetup multi-empresa concluído.")
