# app/routes/company_routes.py - VERSÃO SIMPLIFICADA
from flask import Blueprint, request, jsonify
from app.models.company import Company, CompanyConfig
from app.extensions import db

company_bp = Blueprint('companies', __name__)


@company_bp.route('/', methods=['POST'])
def create_company():
    try:
        data = request.get_json()

        company = Company(
            cnpj=data.get('cnpj'),
            razao_social=data.get('razao_social'),
            nome_fantasia=data.get('nome_fantasia')
        )

        db.session.add(company)
        db.session.commit()

        return jsonify(company.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@company_bp.route('/')
def list_companies():
    companies = Company.query.all()
    return jsonify([company.to_dict() for company in companies])