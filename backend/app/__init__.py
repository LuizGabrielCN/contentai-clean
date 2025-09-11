from flask import Flask
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    
    # Configurações básicas
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-key-123-contentai'
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.config['JSON_SORT_KEYS'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = True  # Para HTTPS
    app.config['REMEMBER_COOKIE_HTTPONLY'] = True
    app.config['REMEMBER_COOKIE_SECURE'] = True
    
    # Habilitar CORS para frontend
    CORS(app, origins=[
        "http://localhost:5000", 
        "http://127.0.0.1:5000", 
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ])
    
    # Registrar blueprints (rotas)
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    print("✅ Aplicação Flask configurada com sucesso!")
    print("🔧 Modo:", "Desenvolvimento" if os.environ.get('FLASK_ENV') == 'development' else "Produção")
    return app