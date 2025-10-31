# app/routes/ml_routes.py - VERSÃO DE TESTE SIMPLIFICADA

from flask import jsonify

def init_ml_routes(app):
    """Inicializa apenas as rotas essenciais para teste."""

    @app.route('/api/ml/analytics/overview')
    def get_ml_overview_test():
        """Rota de teste para o overview."""
        app.logger.info("Acessando rota de teste /api/ml/analytics/overview")
        # Retorna dados falsos para confirmar que a rota funciona
        return jsonify({
            'success': True,
            'data': {
                'total_revenue': 12345.67,
                'total_orders': 907,
                'average_ticket': 13.61
            },
            'message': 'Dados de teste do overview'
        })

    @app.route('/api/ml/vendas', methods=['GET'])
    def get_vendas():
        """Endpoint para buscar vendas reais do DB."""
        from app.models.ml_models import VendaML
        try:
            vendas = VendaML.query.order_by(VendaML.data_venda.desc()).all()
            resultado = [{
                'id_pedido': v.id_pedido,
                'data_venda': v.data_venda.isoformat() if v.data_venda else None,
                'titulo': v.titulo,
                'sku': v.sku,
                'quantidade': v.quantidade,
                'preco_unitario': v.preco_unitario,
                'situacao': v.situacao
            } for v in vendas]
            return jsonify(success=True, data=resultado)
        except Exception as e:
            app.logger.error(f"Erro em /api/ml/vendas: {e}")
            return jsonify(success=False, message=str(e)), 500
