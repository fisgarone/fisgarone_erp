# app/controllers/company_controller.py - CORRIGIDO
from flask import request, jsonify
from app.services.company_service import CompanyService, CompanyConfigService


class CompanyController:
    @staticmethod
    def create_company():
        try:
            data = request.get_json()
            company = CompanyService.create_company(data)
            return jsonify(company.to_dict()), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def list_companies():
        companies = CompanyService.get_all_companies()
        return jsonify([company.to_dict() for company in companies])


class CompanyAutomationController:
    @staticmethod
    def update_config(company_id):
        try:
            data = request.get_json()
            config = CompanyConfigService.update_config(
                company_id,
                data.get('config_key'),
                data.get('config_value')
            )
            return jsonify(config.to_dict()), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400