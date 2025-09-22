from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
import os
import secrets

# ✅ Inicializar SocketIO globalmente
socketio = SocketIO(cors_allowed_origins=[
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "contentai-clean-production.up.railway.app"
])

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

    # ✅ Inicializar SocketIO com a app
    socketio.init_app(app)

    # ✅ Configuração do Banco de Dados
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:RiTbpZhNlEeGlXhbtXuigVwhgTGmtefy@turntable.proxy.rlwy.net:33008/railway')
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

    # ✅ CONFIGURAÇÃO DE EMAIL PARA RESET DE SENHA
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@helpubli.com')

    # ✅ Inicializar Flask-Mail
    try:
        from flask_mail import Mail
        mail = Mail(app)
        print("✅ Flask-Mail configurado para envio de emails")
    except ImportError:
        print("⚠️  Flask-Mail não instalado (emails não funcionam)")
        mail = None

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

    # ✅ Inicializar SocketIO events
    from app.routes import init_socketio
    init_socketio(socketio)

    print("✅ Aplicação Flask configurada com sucesso!")
    print("🔧 Modo:", "Desenvolvimento" if os.environ.get('FLASK_ENV') == 'development' else "Produção")
    print("🗄️  Banco de dados:", app.config['SQLALCHEMY_DATABASE_URI'])
    print("🔐 JWT Configurado:", app.config['JWT_SECRET_KEY'] is not None)
    print("🔌 WebSocket Configurado:", True)
    print("📧 Email Configurado:", mail is not None)

    return app, socketio
