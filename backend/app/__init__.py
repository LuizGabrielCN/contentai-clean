from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
import os

def create_app():
    app = Flask(__name__)
    
    # Configurações básicas
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-key-123-contentai'
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.config['JSON_SORT_KEYS'] = False
    
    # ✅ Configuração do Banco de Dados
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///contentai.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Habilitar CORS para frontend
    CORS(app, origins=[
        "http://localhost:5000", 
        "http://127.0.0.1:5000", 
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://*.railway.app"  # Para produção no Railway
    ])

    # ✅ Inicializar Banco de Dados
    from app.models import db
    db.init_app(app)
    
    migrate = Migrate(app, db)
    
    # ✅ Criar tabelas se não existirem
    with app.app_context():
        db.create_all()
        # Inicializar estatísticas se não existirem
        from app.models import AppStatistics
        if not AppStatistics.query.first():
            stats = AppStatistics()
            db.session.add(stats)
            db.session.commit()

    # Registrar blueprints (rotas)
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    print("✅ Aplicação Flask configurada com sucesso!")
    print("🔧 Modo:", "Desenvolvimento" if os.environ.get('FLASK_ENV') == 'development' else "Produção")
    print("🗄️  Banco de dados:", app.config['SQLALCHEMY_DATABASE_URI'])
    
    return app