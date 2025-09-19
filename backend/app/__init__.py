from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
import secrets

def create_app():
    app = Flask(__name__)
    
    # Configurações básicas
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY') or secrets.token_hex(32)
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hora
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.config['JSON_SORT_KEYS'] = False
    
    
    # ✅ CONFIGURAÇÃO CRÍTICA: Permitir integer como subject
    app.config['JWT_IDENTITY_CLAIM'] = 'sub'  # Garantir que usa 'sub' claim
    app.config['JWT_ALGORITHM'] = 'HS256'     # Definir algoritmo explicitamente
    
    # ✅ Configuração JWT
    jwt = JWTManager(app)
    
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        # user já deve ser o ID (integer) do usuário
        if isinstance(user, int):
            return user
        elif hasattr(user, 'id'):
            return user.id
        else:
            return str(user)  # Fallback seguro
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        from app.models import User
        identity = jwt_data["sub"]
        return User.query.get(identity)
    
    # ✅ Configuração do Banco de Dados
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:robGUHoHsQbVSQINULmIGJuyDDivpJKd@crossover.proxy.rlwy.net:12218/railway')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgresql'):
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'connect_args': {
                'sslmode': 'require'
            }
    }
    
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
    
    # ✅ Importar Migrate
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