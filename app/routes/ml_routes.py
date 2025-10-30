# app/routes/ml_routes.py - IMPORTS CORRETOS
from flask import jsonify, request
from app.services.ml_analytics_service import MLAnalyticsService  # ✅ CORRIGIDO
from app.services.mercado_livre_service import MercadoLivreService  # ✅ CORRIGIDO
import MySQLdb
import os

def init_ml_routes(app):
    """Inicializar rotas do Mercado Livre - FORMA ORIGINAL"""

    @app.route('/api/ml/analytics/overview')
    def get_ml_overview():
        """Dashboard overview"""
        try:
            company_id = request.args.get('company_id', 1, type=int)
            analytics = MLAnalyticsService()
            overview = analytics.get_dashboard_overview(company_id)

            return jsonify({
                'success': True,
                'data': overview,
                'message': 'Dashboard overview carregado'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erro ao carregar dashboard'
            }), 500

    @app.route('/api/ml/analytics/trends')
    def get_ml_trends():
        """Tendências de vendas"""
        try:
            company_id = request.args.get('company_id', 1, type=int)
            analytics = MLAnalyticsService()
            trends = analytics.get_sales_trends(company_id)

            return jsonify({
                'success': True,
                'data': trends,
                'message': 'Tendências carregadas'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erro ao carregar tendências'
            }), 500

    @app.route('/api/ml/analytics/abc')
    def get_ml_abc():
        """Curva ABC"""
        try:
            company_id = request.args.get('company_id', 1, type=int)
            analytics = MLAnalyticsService()
            abc = analytics.calculate_abc_curve(company_id)  # ✅ MÉTODO CORRETO

            return jsonify({
                'success': True,
                'data': abc,
                'message': 'Curva ABC carregada'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erro ao carregar curva ABC'
            }), 500
    @app.route('/api/ml/analytics/divergences')
    def get_ml_divergences():
        """Anomalias"""
        try:
            company_id = request.args.get('company_id', 1, type=int)
            analytics = MLAnalyticsService()
            divergences = analytics.detect_business_anomalies(company_id)  # ✅ CORRETO

            return jsonify({
                'success': True,
                'data': divergences,
                'message': 'Anomalias carregadas'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erro ao carregar anomalias'
            }), 500

    @app.route('/api/ml/analytics/top-items')
    def get_ml_top_items():
        """Top items"""
        try:
            company_id = request.args.get('company_id', 1, type=int)
            analytics = MLAnalyticsService()
            top_items = analytics.get_top_items(company_id)

            return jsonify({
                'success': True,
                'data': top_items,
                'message': 'Top items carregado'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erro ao carregar top items'
            }), 500

    @app.route('/api/ml/sync/<int:company_id>', methods=['POST'])
    def sync_ml_orders(company_id):
        """Sincronizar pedidos ML"""
        try:
            days_back = request.json.get('days_back', 7) if request.json else 7
            ml_service = MercadoLivreService()
            result = ml_service.sync_orders(company_id, days_back)

            return jsonify(result)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erro na sincronização'
            }), 500

    @app.route('/api/ml/sync/status')
    def get_ml_sync_status():
        """Status da sincronização"""
        try:
            company_id = request.args.get('company_id', 1, type=int)

            database_url = os.getenv('DATABASE_URL')
            url_clean = database_url.replace('mysql+pymysql://', '')
            parts = url_clean.split('@')
            user_pass = parts[0].split(':')
            host_db = parts[1].split('/')
            host_port = host_db[0].split(':')

            conn = MySQLdb.connect(
                host=host_port[0],
                port=int(host_port[1]),
                user=user_pass[0],
                passwd=user_pass[1],
                db=host_db[1]
            )

            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM vendas_ml")
            total_vendas = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM vendas_ml WHERE Situacao = 'Pago'")
            vendas_pagas = cursor.fetchone()[0]

            cursor.execute("SELECT MAX(`data_venda`) FROM vendas_ml")  # ✅ CORRETO)
            ultima_venda = cursor.fetchone()[0]

            cursor.close()
            conn.close()

            return jsonify({
                'success': True,
                'data': {
                    'total_vendas': total_vendas,
                    'vendas_pagas': vendas_pagas,
                    'ultima_venda': str(ultima_venda) if ultima_venda else None,
                    'status': 'sincronizado'
                }
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500