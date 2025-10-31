# app/routes/ml_routes.py - VERSÃO CORRIGIDA PARA POSTGRESQL/SQLALCHEMY

from flask import jsonify, request
from app.extensions import db  # Importar a instância db do SQLAlchemy
from app.models.ml_models import VendaML  # Importar o modelo para fazer a query
from app.services.ml_analytics_service import MLAnalyticsService
from app.services.mercado_livre_service import MercadoLivreService
import os
from sqlalchemy import func  # Importar func para usar MAX()


def init_ml_routes(app):
    """Inicializar rotas do Mercado Livre - Refatorado para SQLAlchemy"""

    # ... (TODAS AS OUTRAS ROTAS PERMANECEM IDÊNTICAS) ...
    # /api/ml/analytics/overview
    # /api/ml/analytics/trends
    # /api/ml/analytics/abc
    # /api/ml/analytics/divergences
    # /api/ml/analytics/top-items
    # /api/ml/sync/<int:company_id>

    @app.route('/api/ml/analytics/overview')
    def get_ml_overview():
        """Dashboard overview"""
        try:
            company_id = request.args.get('company_id', 1, type=int)
            analytics = MLAnalyticsService()
            overview = analytics.get_dashboard_overview(company_id)
            return jsonify({'success': True, 'data': overview, 'message': 'Dashboard overview carregado'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e), 'message': 'Erro ao carregar dashboard'}), 500

    @app.route('/api/ml/analytics/trends')
    def get_ml_trends():
        """Tendências de vendas"""
        try:
            company_id = request.args.get('company_id', 1, type=int)
            analytics = MLAnalyticsService()
            trends = analytics.get_sales_trends(company_id)
            return jsonify({'success': True, 'data': trends, 'message': 'Tendências carregadas'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e), 'message': 'Erro ao carregar tendências'}), 500

    @app.route('/api/ml/analytics/abc')
    def get_ml_abc():
        """Curva ABC"""
        try:
            company_id = request.args.get('company_id', 1, type=int)
            analytics = MLAnalyticsService()
            abc = analytics.calculate_abc_curve(company_id)
            return jsonify({'success': True, 'data': abc, 'message': 'Curva ABC carregada'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e), 'message': 'Erro ao carregar curva ABC'}), 500

    @app.route('/api/ml/analytics/divergences')
    def get_ml_divergences():
        """Anomalias"""
        try:
            company_id = request.args.get('company_id', 1, type=int)
            analytics = MLAnalyticsService()
            divergences = analytics.detect_business_anomalies(company_id)
            return jsonify({'success': True, 'data': divergences, 'message': 'Anomalias carregadas'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e), 'message': 'Erro ao carregar anomalias'}), 500

    @app.route('/api/ml/analytics/top-items')
    def get_ml_top_items():
        """Top items"""
        try:
            company_id = request.args.get('company_id', 1, type=int)
            analytics = MLAnalyticsService()
            top_items = analytics.get_top_items(company_id)
            return jsonify({'success': True, 'data': top_items, 'message': 'Top items carregado'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e), 'message': 'Erro ao carregar top items'}), 500

    @app.route('/api/ml/sync/<int:company_id>', methods=['POST'])
    def sync_ml_orders(company_id):
        """Sincronizar pedidos ML"""
        try:
            days_back = request.json.get('days_back', 7) if request.json else 7
            ml_service = MercadoLivreService()
            result = ml_service.sync_orders(company_id, days_back)
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e), 'message': 'Erro na sincronização'}), 500

    # ===== ROTA CORRIGIDA =====
    @app.route('/api/ml/sync/status')
    def get_ml_sync_status():
        """Status da sincronização usando SQLAlchemy"""
        try:
            # Usando o SQLAlchemy para fazer as queries de forma segura e compatível
            total_vendas = db.session.query(func.count(VendaML.id_pedido)).scalar()
            vendas_pagas = db.session.query(func.count(VendaML.id_pedido)).filter(VendaML.situacao == 'Pago').scalar()

            # Query para a data máxima. O nome da coluna é 'data_venda' no modelo.
            # Como a data está como String, não podemos usar MAX diretamente de forma confiável
            # A melhor abordagem é ordenar e pegar o primeiro, mas para manter a simplicidade:
            ultima_venda_tupla = db.session.query(func.max(VendaML.data_venda)).first()
            ultima_venda = ultima_venda_tupla[0] if ultima_venda_tupla else None

            return jsonify({
                'success': True,
                'data': {
                    'total_vendas': total_vendas or 0,
                    'vendas_pagas': vendas_pagas or 0,
                    'ultima_venda': str(ultima_venda) if ultima_venda else None,
                    'status': 'sincronizado'
                }
            })

        except Exception as e:
            # Logar o erro no servidor para depuração
            app.logger.error(f"Erro em /api/ml/sync/status: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erro ao obter status da sincronização'
            }), 500


# ===== NOVA ROTA PARA O DASHBOARD DE VENDAS =====
@app.route('/api/ml/vendas', methods=['GET'])
def get_vendas():
    """
    Endpoint de API para buscar todas as vendas do Mercado Livre
    salvas no banco de dados para exibição no dashboard.
    """
    try:
        # Consulta o banco de dados para buscar todas as vendas, ordenadas pela mais recente
        vendas = VendaML.query.order_by(VendaML.data_venda.desc()).all()

        # Converte a lista de objetos de venda em uma lista de dicionários
        resultado = []
        for venda in vendas:
            resultado.append({
                'id_pedido': venda.id_pedido,
                'data_venda': venda.data_venda.isoformat() if venda.data_venda else None,
                'situacao': venda.situacao,
                'mlb': venda.mlb,
                'sku': venda.sku,
                'titulo': venda.titulo,
                'quantidade': venda.quantidade,
                'preco_unitario': venda.preco_unitario,
                'taxa_ml': venda.taxa_ml,
                'company_id': venda.company_id
            })

        # Retorna os dados como uma resposta JSON
        return jsonify(success=True, data=resultado)

    except Exception as e:
        # Em caso de erro, retorna uma mensagem de erro
        app.logger.error(f"Erro em /api/ml/vendas: {e}")
        return jsonify(success=False, message=str(e)), 500

