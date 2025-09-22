import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS  # ✅ Importar o CORS
from flask_socketio import SocketIO
from flask_mail import Mail
from flask_bcrypt import Bcrypt

# Inicializar extensões
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
socketio = SocketIO()
mail = Mail()
bcrypt = Bcrypt()

def create_app():
    """Cria e configura a aplicação Flask."""
    app = Flask(__name__, static_folder='../../frontend', static_url_path='/')

    # --- Configurações ---
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'uma-chave-secreta-muito-forte')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'outra-chave-secreta-jwt')

    # Configuração do Flask-Mail
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

    # ✅ --- Configuração do CORS ---
    # Permite que todas as origens acessem a API. Para produção, você pode restringir
    # para o domínio do seu frontend, ex: CORS(app, origins="https://seu-dominio.com")
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    print("✅ CORS configurado para permitir todas as origens em /api/*")

    # --- Inicializar Extensões ---
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    
    # Importar e registrar Blueprints (rotas)
    from .routes import main_bp, init_socketio, init_cache_cleaner
    app.register_blueprint(main_bp)

    # Inicializar SocketIO com CORS permitido para todas as origens
    socketio.init_app(app, cors_allowed_origins="*")
    init_socketio(socketio)
    print("✅ WebSocket (SocketIO) configurado com CORS")

    # Inicializar limpeza de cache
    init_cache_cleaner(app)

    # Rota para servir o index.html
    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    @app.route('/admin')
    def admin_page():
        return app.send_static_file('admin-dashboard.html')

    return app, socketio