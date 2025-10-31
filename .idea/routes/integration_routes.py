# app/routes/integration_routes.py - VERSÃO FUNCIONAL SIMPLES
from flask import Blueprint, jsonify

integration_bp = Blueprint('integration', __name__)

@integration_bp.route('/status')
def integration_status():
    return jsonify({
        'success': True,
        'message': 'Módulo de integração ativo'
    })