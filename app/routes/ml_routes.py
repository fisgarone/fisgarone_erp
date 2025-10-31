# app/routes/ml_routes.py - REESTRUTURADO PARA BLUEPRINT

from flask import Blueprint, jsonify
from app.models.ml_models import VendaML

ml_bp = Blueprint('ml_bp', __name__)

@ml_bp.route('/analytics/overview')
def get_ml_overview():
    # Por enquanto, retorna dados de teste para validar a rota
    return jsonify({'success': True, 'data': {'total_revenue': 12345.67}})

@ml_bp.route('/analytics/trends')
def get_ml_trends():
    return jsonify({'success': True, 'data': []}) # Retorno de teste

@ml_bp.route('/analytics/abc')
def get_ml_abc():
    return jsonify({'success': True, 'data': []}) # Retorno de teste

@ml_bp.route('/vendas')
def get_vendas():
    try:
        vendas = VendaML.query.order_by(VendaML.data_venda.desc()).all()
        resultado = [{'id_pedido': v.id_pedido, 'titulo': v.titulo} for v in vendas]
        return jsonify(success=True, data=resultado)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500
