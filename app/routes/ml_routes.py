# app/routes/ml_routes.py - VERSÃO FINAL E COMPLETA

from flask import Blueprint, jsonify
from app.models.ml_models import VendaML
from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)
ml_bp = Blueprint('ml_bp', __name__)


@ml_bp.route('/vendas', methods=['GET'])
def get_vendas():
    """
    Endpoint de API para buscar todas as vendas do Mercado Livre
    salvas no banco de dados. Esta é a fonte de dados para o dashboard.
    """
    try:
        vendas = VendaML.query.order_by(VendaML.data_venda.desc()).all()
        resultado = [{
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
        } for venda in vendas]

        return jsonify(success=True, data=resultado)

    except SQLAlchemyError as e:
        logger.error(f"Erro de banco de dados em /api/ml/vendas: {e}")
        return jsonify(success=False, message="Erro ao consultar o banco de dados."), 500
    except Exception as e:
        logger.error(f"Erro inesperado em /api/ml/vendas: {e}")
        return jsonify(success=False, message="Erro interno do servidor."), 500


# Adicionando rotas de analytics de teste para evitar erros 404 no frontend
@ml_bp.route('/analytics/overview')
def get_ml_overview_placeholder():
    # Retorna uma estrutura mínima para não quebrar o frontend
    return jsonify({'success': True, 'data': {'kpis': [
        {'name': 'Total de Vendas', 'value': 0, 'unit': ''},
        {'name': 'Faturamento Bruto', 'value': 0, 'unit': 'R$'},
        {'name': 'Faturamento Líquido', 'value': 0, 'unit': 'R$'},
        {'name': 'Ticket Médio', 'value': 0, 'unit': 'R$'},
        {'name': 'Lucro Estimado', 'value': 0, 'unit': 'R$'}
    ]}})


@ml_bp.route('/analytics/trends')
def get_ml_trends_placeholder():
    return jsonify({'success': True, 'data': {'sales_data': []}})


@ml_bp.route('/analytics/abc')
def get_ml_abc_placeholder():
    return jsonify({'success': True, 'data': {'items': []}})


@ml_bp.route('/analytics/top-items')
def get_ml_top_items_placeholder():
    return jsonify({'success': True, 'data': []})


@ml_bp.route('/sync/status')
def get_ml_sync_status_placeholder():
    return jsonify({'success': True, 'data': {'status': 'idle'}})
