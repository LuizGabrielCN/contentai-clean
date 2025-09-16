from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class GenerationHistory(db.Model):
    __tablename__ = 'generation_history'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # 'ideas' or 'script'
    data = db.Column(db.Text, nullable=False)  # JSON data as string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_session = db.Column(db.String(100), default='default')
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'data': json.loads(self.data),
            'created_at': self.created_at.isoformat(),
            'user_session': self.user_session
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