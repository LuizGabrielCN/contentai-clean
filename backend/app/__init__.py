from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager  # ✅ IMPORTE AQUI
import os

def create_app():
    app = Flask(__name__)
    
    # Configurações básicas
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-key-123-contentai'
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-123'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hora
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.config['JSON_SORT_KEYS'] = False
    
    # ✅ Configuração JWT (AGORA FUNCIONARÁ)
    jwt = JWTManager(app)
    
    # ✅ Configuração do Banco de Dados
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///contentai.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Habilitar CORS para frontend
    CORS(app, origins=[
        "http://localhost:5000", 
        "http://127.0.0.1:5000", 
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "contentai-clean-production.up.railway.app"
    ])

    # ✅ Inicializar Banco de Dados
    from app.models import db
    db.init_app(app)
    
    # ✅ Importar Migrate somente quando necessário
    try:
        from flask_migrate import Migrate
        migrate = Migrate(app, db)
        print("✅ Flask-Migrate configurado")
    except ImportError:
        print("⚠️  Flask-Migrate não instalado (modo sem migrações)")
        migrate = None
    
    # ✅ Inicializar Bcrypt
    from app.models import bcrypt
    bcrypt.init_app(app)
    
    # ✅ Criar tabelas se não existirem
    with app.app_context():
        db.create_all()
        from app.models import AppStatistics
        if not AppStatistics.query.first():
            stats = AppStatistics()
            db.session.add(stats)
            db.session.commit()

    # Registrar blueprints (rotas)
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    # ✅ Inicializar limpeza de cache
    from app.routes import init_cache_cleaner
    init_cache_cleaner(app)
    
    print("✅ Aplicação Flask configurada com sucesso!")
    print("🔧 Modo:", "Desenvolvimento" if os.environ.get('FLASK_ENV') == 'development' else "Produção")
    print("🗄️  Banco de dados:", app.config['SQLALCHEMY_DATABASE_URI'])
    print("🔐 JWT Configurado:", app.config['JWT_SECRET_KEY'] is not None)
    
    return app