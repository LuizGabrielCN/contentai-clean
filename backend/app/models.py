from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
from flask import current_app
import json
import jwt

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'users'

    # ... (campos existentes)
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_premium = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)

    # Campos para reset de senha
    reset_token = db.Column(db.String(256), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    
    # Relação com histórico
    generations = db.relationship('GenerationHistory', backref='user', lazy=True)

    __table_args__ = (
        db.UniqueConstraint('reset_token', name='uq_user_reset_token'),
    )
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def generate_reset_token(self):
        """Gera um token de reset de senha seguro e com tempo de expiração."""
        secret_key = current_app.config['SECRET_KEY']
        payload = {
            'user_id': self.id,
            'exp': datetime.utcnow() + timedelta(hours=1)  # Expira em 1 hora
        }
        self.reset_token = jwt.encode(payload, secret_key, algorithm='HS256')
        self.reset_token_expires = payload['exp']
        return self.reset_token

    @staticmethod
    def verify_reset_token(token):
        """Verifica o token de reset e retorna o usuário se for válido."""
        secret_key = current_app.config['SECRET_KEY']
        user = User.query.filter_by(reset_token=token).first()
        if user and user.reset_token_expires > datetime.utcnow():
            return user
        return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'is_premium': self.is_premium,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class GenerationHistory(db.Model):
    __tablename__ = 'generation_history'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)
    data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # ✅ Nova relação
    user_session = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'data': json.loads(self.data),
            'created_at': self.created_at.isoformat(),
            'user_id': self.user_id
        }

class UserFeedback(db.Model):
    __tablename__ = 'user_feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer)  # 1-5 stars
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_session = db.Column(db.String(100), default='default')
    
    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'rating': self.rating,
            'created_at': self.created_at.isoformat()
        }

class AppStatistics(db.Model):
    __tablename__ = 'app_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    total_ideas_generated = db.Column(db.Integer, default=0)
    total_scripts_generated = db.Column(db.Integer, default=0)
    total_feedbacks = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'total_ideas_generated': self.total_ideas_generated,
            'total_scripts_generated': self.total_scripts_generated,
            'total_feedbacks': self.total_feedbacks,
            'last_updated': self.last_updated.isoformat()
        }