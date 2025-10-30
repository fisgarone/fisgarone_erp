# app/services/company_service.py - CORRIGIDO
from app.models.company import Company, CompanyConfig, IntegrationConfig  # Mudar company_model para company
from app.extensions import db


class CompanyService:
    @staticmethod
    def create_company(data):
        company = Company(
            cnpj=data.get('cnpj'),
            razao_social=data.get('razao_social'),
            nome_fantasia=data.get('nome_fantasia')
        )
        db.session.add(company)
        db.session.commit()
        return company

    @staticmethod
    def get_all_companies():
        return Company.query.all()

    @staticmethod
    def get_company_by_id(company_id):
        return Company.query.get(company_id)


class CompanyConfigService:
    @staticmethod
    def update_config(company_id, config_key, config_value):
        config = CompanyConfig.query.filter_by(
            company_id=company_id,
            config_key=config_key
        ).first()

        if not config:
            config = CompanyConfig(company_id=company_id, config_key=config_key)

        config.config_value = config_value
        db.session.add(config)
        db.session.commit()
        return config