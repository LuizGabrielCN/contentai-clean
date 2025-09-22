import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Configurar Flask app similar ao principal
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:RiTbpZhNlEeGlXhbtXuigVwhgTGmtefy@turntable.proxy.rlwy.net:33008/railway')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Se for PostgreSQL, adicionar SSL
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgresql'):
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'connect_args': {
            'sslmode': 'require'
        }
    }

db = SQLAlchemy(app)

# Modelo User (cópia do app.models)
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100))
    is_premium = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    last_login = db.Column(db.DateTime)

with app.app_context():
    # Encontrar usuário por email
    email = 'lbiel213@gmail.com'
    user = User.query.filter_by(email=email).first()

    if user:
        # Tornar admin e premium
        user.is_admin = True
        user.is_premium = True
        db.session.commit()
        print(f"Usuário {email} atualizado para admin e premium!")
        print(f"ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Nome: {user.name}")
        print(f"Admin: {user.is_admin}")
        print(f"Premium: {user.is_premium}")
    else:
        print(f"Usuário {email} não encontrado!")
