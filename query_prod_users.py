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
    # Executar consulta
    users = User.query.all()

    # Imprimir cabeçalhos
    print("ID | Email | Name | Premium | Admin | Created At | Last Login")
    print("-" * 80)

    # Imprimir cada usuário
    for user in users:
        print(f"{user.id} | {user.email} | {user.name or 'N/A'} | {user.is_premium} | {user.is_admin} | {user.created_at} | {user.last_login or 'Never'}")
