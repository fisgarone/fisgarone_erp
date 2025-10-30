# test_server.py - Servidor simples para testar frontend
from flask import Flask, send_from_directory, jsonify
import json
import os

app = Flask(__name__, static_folder='frontend', template_folder='frontend')

# ===== ROTAS DO FRONTEND =====
@app.route('/')
def serve_frontend():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)

# ===== MOCK API - Para testar frontend sem o backend completo =====
@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'online',
        'service': 'FISGARONE AI',
        'version': '1.0.0'
    })

@app.route('/api/ml/analytics/overview')
def mock_overview():
    """Mock dos dados de overview"""
    return jsonify({
        'success': True,
        'data': {
            'kpis': [
                {'name': 'Total de Vendas', 'value': 38, 'unit': 'vendas'},
                {'name': 'Faturamento Bruto', 'value': 2522.73, 'unit': 'R$'},
                {'name': 'Faturamento Líquido', 'value': 2144.32, 'unit': 'R$'},
                {'name': 'Ticket Médio', 'value': 74.20, 'unit': 'R$'},
                {'name': 'Lucro Estimado', 'value': 643.30, 'unit': 'R$'}
            ]
        }
    })

@app.route('/api/ml/analytics/trends')
def mock_trends():
    """Mock dos dados de tendências"""
    return jsonify({
        'success': True,
        'data': {
            'daily_data': [
                {'date': '2025-10-21', 'total_sales': 769.26},
                {'date': '2025-10-22', 'total_sales': 310.48},
                {'date': '2025-10-23', 'total_sales': 115.75},
                {'date': '2025-10-24', 'total_sales': 75.27},
                {'date': '2025-10-25', 'total_sales': 72.66}
            ]
        }
    })

@app.route('/api/ml/analytics/abc')
def mock_abc():
    """Mock da curva ABC"""
    return jsonify({
        'success': True,
        'data': {
            'items': [
                {'title': 'Kit Festa 200 Lembrancinha', 'total_sales': 375.18, 'classification': 'A'},
                {'title': 'Kit Sacolinha Aniversario', 'total_sales': 245.85, 'classification': 'B'},
                {'title': 'Kit Lembrancinha Surpresa', 'total_sales': 170.61, 'classification': 'B'}
            ]
        }
    })

@app.route('/api/ml/analytics/top-items')
def mock_top_items():
    """Mock do top items"""
    return jsonify({
        'success': True,
        'data': {
            'items': [
                {'title': 'Kit Festa 200 Lembrancinha', 'total_sales': 375.18, 'total_profit': 112.55},
                {'title': 'Kit Sacolinha Aniversario', 'total_sales': 245.85, 'total_profit': 73.76},
                {'title': 'Kit Lembrancinha Surpresa', 'total_sales': 170.61, 'total_profit': 51.18}
            ]
        }
    })

@app.route('/api/ml/sync/status')
def mock_sync_status():
    """Mock do status de sincronização"""
    return jsonify({
        'success': True,
        'data': {
            'total_vendas': 38,
            'vendas_pagas': 34,
            'ultima_venda': '2025-10-25',
            'status': 'sincronizado'
        }
    })

if __name__ == '__main__':
    print("🚀 SERVIDOR TESTE FISGARONE AI INICIADO!")
    print("🎨 Frontend: http://localhost:5001/")
    print("📚 Mock API: http://localhost:5001/api/")
    print("🔧 Este é um servidor temporário para testar o frontend")
    app.run(debug=True, host='0.0.0.0', port=5001)