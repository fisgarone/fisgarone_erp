from flask import Flask, send_from_directory, jsonify
from datetime import datetime
import os
import sys

# Configurar path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

app = Flask(__name__,
            static_folder='frontend',  # ← MUDEI PARA FRONTEND
            static_url_path='',
            template_folder='frontend'  # ← MUDEI PARA FRONTEND
            )

# ===== CONFIGURAÇÃO DO BANCO =====
try:
    from app.extensions import db, migrate

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    migrate.init_app(app, db)
    print("✅ Banco de dados configurado")
except Exception as e:
    print(f"⚠️  Aviso banco de dados: {e}")

# ===== INICIALIZAR ROTAS =====
try:
    from app.routes.ml_routes import init_ml_routes

    init_ml_routes(app)
    print("✅ Rotas ML carregadas")
except Exception as e:
    print(f"❌ Erro rotas ML: {e}")

try:
    from app.routes.company_routes import company_bp

    app.register_blueprint(company_bp, url_prefix='/api/companies')
    print("✅ Rotas Company carregadas")
except Exception as e:
    print(f"❌ Erro rotas Company: {e}")


# ===== ROTAS DO FRONTEND - CORRIGIDAS PARA PASTA FRONTEND =====
@app.route('/')
def serve_index():
    try:
        return send_from_directory('frontend', 'index.html')
    except Exception as e:
        return f"Erro ao carregar index.html: {e}", 500


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)


# ===== ROTA HEALTH CHECK =====
@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "FISGARONE ERP Online",
        "timestamp": datetime.now().isoformat(),
        "frontend_path": "frontend/",
        "estrutura": "✅ Backend + Frontend integrados"
    })


if __name__ == '__main__':
    print("🚀 FISGARONE ERP - SERVIDOR CORRIGIDO")
    print("📍 Frontend: http://localhost:5000")
    print("📁 Pasta frontend:", os.path.abspath('frontend'))

    # Listar arquivos do frontend para debug
    try:
        frontend_files = os.listdir('frontend')
        print("📄 Arquivos no frontend:", [f for f in frontend_files if f.endswith(('.html', '.css', '.js'))])
    except Exception as e:
        print(f"❌ Erro ao acessar pasta frontend: {e}")

    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"❌ Erro: {e}")