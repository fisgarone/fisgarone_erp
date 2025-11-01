# app/routes/ml_routes.py - VERSÃO FINAL, CUMPRINDO O CONTRATO DO FRONTEND

from flask import jsonify, request
from app.extensions import db
from app.models.ml_models import VendaML
from app.services.ml_analytics_service import MLAnalyticsService
from app.services.mercado_livre_service import MercadoLivreService
from sqlalchemy import func

def init_ml_routes(app):
    """Inicializa as rotas de API, retornando os dados no formato exato esperado pelo frontend."""

    @app.route('/api/ml/analytics/overview')
    def get_ml_overview():
        """
        CONTRATO: Retorna { "data": { "kpis": [...] } }
        """
        try:
            company_id = request.args.get('company_id', 1, type=int)
            analytics = MLAnalyticsService()
            overview_data = analytics.get_dashboard_overview(company_id)
            # Retorna o objeto diretamente, que já contém a chave "kpis"
            return jsonify({'data': overview_data})
        except Exception as e:
            app.logger.error(f"Erro em /api/ml/analytics/overview: {e}")
            return jsonify({'data': {'kpis': []}, 'error': str(e)}), 500

    @app.route('/api/ml/analytics/trends')
    def get_ml_trends():
        """
        CONTRATO: Retorna { "data": [...] }
        """
        try:
            company_id = request.args.get('company_id', 1, type=int)
            analytics = MLAnalyticsService()
            trends_data = analytics.get_sales_trends(company_id)
            # Retorna o array diretamente dentro da chave "data"
            return jsonify({'data': trends_data})
        except Exception as e:
            app.logger.error(f"Erro em /api/ml/analytics/trends: {e}")
            return jsonify({'data': [], 'error': str(e)}), 500

    @app.route('/api/ml/analytics/abc')
    def get_ml_abc():
        """
        CONTRATO: Retorna { "data": { "produtos": [...] } }
        """
        try:
            company_id = request.args.get('company_id', 1, type=int)
            analytics = MLAnalyticsService()
            abc_data = analytics.calculate_abc_curve(company_id)
            # Retorna o objeto diretamente, que já contém a chave "produtos"
            return jsonify({'data': abc_data})
        except Exception as e:
            app.logger.error(f"Erro em /api/ml/analytics/abc: {e}")
            return jsonify({'data': {'produtos': []}, 'error': str(e)}), 500

    # As rotas abaixo não são críticas para a renderização inicial do dashboard
    @app.route('/api/ml/sync/<int:company_id>', methods=['POST'])
    def sync_ml_orders(company_id):
        # ... (código original sem alterações)
        pass

    @app.route('/api/ml/sync/status')
    def get_ml_sync_status():
        # ... (código original sem alterações)
        pass
