from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Professional(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    profession = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False, default='São Paulo')
    state = db.Column(db.String(2), nullable=False, default='SP')
    rating = db.Column(db.Float, default=0.0)
    reviews = db.Column(db.Integer, default=0)
    
    # Relacionamentos
    subscription = db.relationship('Subscription', backref='professional', uselist=False, cascade="all, delete-orphan")
    schedules = db.relationship('Schedule', backref='professional', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Professional {self.name} ({self.id})>'

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.String, db.ForeignKey('professional.id'), unique=True, nullable=False)
    plan = db.Column(db.String(50), nullable=False) # Ex: 'Master', 'Profissional'
    status = db.Column(db.String(50), default='active') # Ex: 'active', 'inactive_inadimplencia'
    due_date = db.Column(db.Date, nullable=True) # Data de vencimento

    def __repr__(self):
        return f'<Subscription {self.professional_id} - {self.plan} ({self.status})>'

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.String, db.ForeignKey('professional.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='BLOCKED') # Ex: 'BLOCKED', 'RELEASED'

    def __repr__(self):
        return f'<Schedule {self.professional_id} - {self.start_time.strftime("%Y-%m-%d %H:%M")}>'

