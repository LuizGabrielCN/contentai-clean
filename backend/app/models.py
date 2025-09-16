from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt
import json

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_premium = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    
    # Relação com histórico
    generations = db.relationship('GenerationHistory', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'is_premium': self.is_premium,
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