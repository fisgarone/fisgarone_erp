# app/routes/ml_routes.py - VERSÃO FINAL, ALINHADA COM O CONTRATO DO FRONTEND

from flask import jsonify, request
from app.extensions import db
from app.models.ml_models import VendaML
from app.services.ml_analytics_service import MLAnalyticsService
from app.services.mercado_livre_service import MercadoLivreService
from sqlalchemy import func

def init_ml_routes(app):
    """Inicializa as rotas de API do Mercado Livre, garantindo o formato de resposta correto."""

    @app.route('/api/ml/analytics/overview')
    def get_ml_overview():
        """Dashboard overview - Empacota a resposta para o frontend."""
        try:
            company_id = request.args.get('company_id', 1, type=int)
            analytics = MLAnalyticsService()
            # A função original retorna: { "kpis": [...], "raw_data": {...} }
            overview_data = analytics.get_dashboard_overview(company_id)
            # Empacotamos no formato que o frontend espera: { "data": { "kpis": [...] } }
            return jsonify({'success': True, 'data': overview_data})
        except Exception as e:
            app.logger.error(f"Erro em /api/ml/analytics/overview: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/ml/analytics/trends')
    def get_ml_trends():
        """Tendências de vendas - Empacota a resposta para o frontend."""
        try:
            company_id = request.args.get('company_id', 1, type=int)
            analytics = MLAnalyticsService()
            # A função original retorna um array: [...]
            trends_data = analytics.get_sales_trends(company_id)
            # Empacotamos no formato que o frontend espera: { "data": [...] }
            return jsonify({'success': True, 'data': trends_data})
        except Exception as e:
            app.logger.error(f"Erro em /api/ml/analytics/trends: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/ml/analytics/abc')
    def get_ml_abc():
        """Curva ABC - Empacota a resposta para o frontend."""
        try:
            company_id = request.args.get('company_id', 1, type=int)
            analytics = MLAnalyticsService()
            # A função original retorna: { "produtos": [...], ... }
            abc_data = analytics.calculate_abc_curve(company_id)
            # Empacotamos no formato que o frontend espera: { "data": { "produtos": [...] } }
            return jsonify({'success': True, 'data': abc_data})
        except Exception as e:
            app.logger.error(f"Erro em /api/ml/analytics/abc: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    # As rotas abaixo já estão corretas ou não são usadas pelo dashboard principal
    @app.route('/api/ml/sync/<int:company_id>', methods=['POST'])
    def sync_ml_orders(company_id):
        try:
            days_back = request.json.get('days_back', 7) if request.json else 7
            ml_service = MercadoLivreService()
            result = ml_service.sync_orders(company_id, days_back)
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/ml/sync/status')
    def get_ml_sync_status():
        try:
            total_vendas = db.session.query(func.count(VendaML.id_pedido)).scalar()
            ultima_venda_tupla = db.session.query(func.max(VendaML.data_venda)).first()
            ultima_venda = ultima_venda_tupla[0] if ultima_venda_tupla else None
            return jsonify({
                'success': True,
                'data': {
                    'total_vendas': total_vendas or 0,
                    'ultima_venda': str(ultima_venda) if ultima_venda else None,
                }
            })
        except Exception as e:
            app.logger.error(f"Erro em /api/ml/sync/status: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
