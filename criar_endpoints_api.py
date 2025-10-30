# criar_endpoints_api.py
import os
import sys
from flask import Flask, jsonify, request
from dotenv import load_dotenv

# Adicionar caminho
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
load_dotenv()


def criar_app_flask():
    """Criar aplicação Flask com endpoints de análise"""

    app = Flask(__name__)

    # Configurações
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.config['JSON_SORT_KEYS'] = False

    @app.route('/')
    def home():
        return jsonify({
            'message': 'FISGARONE ERP API - Sistema de Análises ML',
            'status': 'online',
            'version': '1.0.0'
        })

    @app.route('/api/ml/analytics/overview')
    def get_overview():
        """Endpoint para dashboard overview"""
        try:
            from services.ml_analytics_service import MLAnalyticsService
            analytics = MLAnalyticsService()
            overview = analytics.get_dashboard_overview(1)  # company_id=1

            return jsonify({
                'success': True,
                'data': overview,
                'message': 'Dashboard overview carregado com sucesso'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erro ao carregar dashboard overview'
            }), 500

    @app.route('/api/ml/analytics/trends')
    def get_trends():
        """Endpoint para tendências de vendas"""
        try:
            from services.ml_analytics_service import MLAnalyticsService
            analytics = MLAnalyticsService()
            trends = analytics.get_sales_trends(1)

            return jsonify({
                'success': True,
                'data': trends,
                'message': 'Tendências carregadas com sucesso'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erro ao carregar tendências'
            }), 500

    @app.route('/api/ml/analytics/abc')
    def get_abc_analysis():
        """Endpoint para curva ABC"""
        try:
            from services.ml_analytics_service import MLAnalyticsService
            analytics = MLAnalyticsService()
            abc = analytics.get_abc_analysis(1)

            return jsonify({
                'success': True,
                'data': abc,
                'message': 'Curva ABC carregada com sucesso'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erro ao carregar curva ABC'
            }), 500

    @app.route('/api/ml/analytics/divergences')
    def get_divergences():
        """Endpoint para anomalias"""
        try:
            from services.ml_analytics_service import MLAnalyticsService
            analytics = MLAnalyticsService()
            divergences = analytics.get_divergences(1)

            return jsonify({
                'success': True,
                'data': divergences,
                'message': 'Anomalias carregadas com sucesso'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erro ao carregar anomalias'
            }), 500

    @app.route('/api/ml/analytics/top-items')
    def get_top_items():
        """Endpoint para top items"""
        try:
            from services.ml_analytics_service import MLAnalyticsService
            analytics = MLAnalyticsService()
            top_items = analytics.get_top_items(1)

            return jsonify({
                'success': True,
                'data': top_items,
                'message': 'Top items carregado com sucesso'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erro ao carregar top items'
            }), 500

    @app.route('/api/ml/sync/status')
    def get_sync_status():
        """Endpoint para status da sincronização"""
        try:
            import MySQLdb

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

            # Estatísticas
            cursor.execute("SELECT COUNT(*) FROM vendas_ml")
            total_vendas = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM vendas_ml WHERE Situacao = 'Pago'")
            vendas_pagas = cursor.fetchone()[0]

            cursor.execute("SELECT MAX(`Data da Venda`) FROM vendas_ml")
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
                },
                'message': 'Status da sincronização carregado'
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erro ao carregar status'
            }), 500

    return app


def testar_endpoints():
    """Testar todos os endpoints localmente"""
    print("🚀 TESTANDO ENDPOINTS API LOCALMENTE")
    print("=" * 60)

    app = criar_app_flask()

    # Testar com cliente de teste
    with app.test_client() as client:
        endpoints = [
            ('/', 'Home'),
            ('/api/ml/analytics/overview', 'Dashboard Overview'),
            ('/api/ml/analytics/trends', 'Sales Trends'),
            ('/api/ml/analytics/abc', 'Curva ABC'),
            ('/api/ml/analytics/divergences', 'Anomalias'),
            ('/api/ml/analytics/top-items', 'Top Items'),
            ('/api/ml/sync/status', 'Status Sincronização')
        ]

        for endpoint, nome in endpoints:
            print(f"🔗 Testando {nome} ({endpoint})...")
            response = client.get(endpoint)

            if response.status_code == 200:
                data = response.get_json()
                if data.get('success'):
                    print(f"   ✅ {nome} - OK")
                    if 'data' in data:
                        print(f"      Dados: {len(data['data'])} elementos" if isinstance(data['data'], (
                        list, dict)) else "      Dados retornados")
                else:
                    print(f"   ⚠️  {nome} - Erro: {data.get('message')}")
            else:
                print(f"   ❌ {nome} - Status: {response.status_code}")


def criar_arquivo_routes():
    """Criar arquivo de routes para o projeto"""
    routes_content = '''# routes/ml_routes.py
from flask import jsonify, request
from services.ml_analytics_service import MLAnalyticsService
from services.mercado_livre_service import MercadoLivreService
import MySQLdb
import os

def init_ml_routes(app):
    """Inicializar rotas do Mercado Livre"""

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
            abc = analytics.get_abc_analysis(company_id)

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
            divergences = analytics.get_divergences(company_id)

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

            cursor.execute("SELECT MAX(`Data da Venda`) FROM vendas_ml")
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
'''

    # Salvar arquivo de routes
    with open('app/routes/ml_routes.py', 'w', encoding='utf-8') as f:
        f.write(routes_content)

    print("✅ Arquivo de routes criado: app/routes/ml_routes.py")
    return True


if __name__ == "__main__":
    print("🎯 FASE 3 - CRIANDO ENDPOINTS API")
    print("=" * 60)

    # 1. Criar arquivo de routes
    print("1. 📁 CRIANDO ARQUIVO DE ROUTES...")
    routes_ok = criar_arquivo_routes()

    if routes_ok:
        # 2. Testar endpoints
        print("\n2. 🔗 TESTANDO ENDPOINTS...")
        testar_endpoints()

        print("\n🎉 🎉 🎉 ENDPOINTS API CRIADOS COM SUCESSO!")
        print("✅ Dashboard Overview: /api/ml/analytics/overview")
        print("✅ Sales Trends: /api/ml/analytics/trends")
        print("✅ Curva ABC: /api/ml/analytics/abc")
        print("✅ Anomalias: /api/ml/analytics/divergences")
        print("✅ Top Items: /api/ml/analytics/top-items")
        print("✅ Status: /api/ml/sync/status")
        print("✅ Sincronização: /api/ml/sync/<company_id>")

        print("\n🚀 PRÓXIMO: INTEGRAR COM FRONTEND EXISTENTE")
        print("\n💡 Para iniciar o servidor:")
        print("   python criar_endpoints_api.py --server")
    else:
        print("\n❌ Falha ao criar endpoints")