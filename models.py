from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()

class Professional(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    profession = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False, default='São Paulo')
    state = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.Float, default=0.0)
    reviews = db.Column(db.Integer, default=0)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    # Relacionamentos
    subscription = db.relationship('Subscription', backref='professional', uselist=False, cascade="all, delete-orphan")
    schedules = db.relationship('Schedule', backref='professional', lazy='dynamic', cascade="all, delete-orphan")
    metrics = db.relationship('ProfessionalMetrics', backref='professional', uselist=False, cascade="all, delete-orphan")

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

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String, nullable=False)  # ID do cliente
    professional_id = db.Column(db.String, db.ForeignKey('professional.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Localização do cliente
    client_latitude = db.Column(db.Float, nullable=True)
    client_longitude = db.Column(db.Float, nullable=True)
    client_address = db.Column(db.String(255), nullable=True)  # Endereço formatado
    
    # Relacionamentos
    messages = db.relationship('Message', backref='chat', lazy='dynamic', cascade="all, delete-orphan", order_by="Message.sent_at")
    professional = db.relationship('Professional', backref='chats')

    def __repr__(self):
        return f'<Chat {self.id} - Client: {self.client_id}, Professional: {self.professional_id}>'

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    sender_id = db.Column(db.String, nullable=False)  # ID do remetente (cliente ou profissional)
    sender_type = db.Column(db.String(20), nullable=False)  # 'client' ou 'professional'
    content = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Message {self.id} - Chat: {self.chat_id}, From: {self.sender_type}>'

class ProfessionalMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.String, db.ForeignKey('professional.id'), unique=True, nullable=False)
    
    # Métricas de visualização
    profile_views = db.Column(db.Integer, default=0)  # Visualizações do perfil
    profile_views_this_month = db.Column(db.Integer, default=0)  # Visualizações este mês
    
    # Métricas de conversão
    whatsapp_clicks = db.Column(db.Integer, default=0)  # Cliques no botão WhatsApp
    whatsapp_clicks_this_month = db.Column(db.Integer, default=0)  # Cliques este mês
    
    # Métricas de chat
    chat_conversations = db.Column(db.Integer, default=0)  # Total de conversas iniciadas
    chat_conversations_this_month = db.Column(db.Integer, default=0)  # Conversas este mês
    
    # Métricas de agendamento
    total_appointments = db.Column(db.Integer, default=0)  # Total de agendamentos
    appointments_this_month = db.Column(db.Integer, default=0)  # Agendamentos este mês
    completed_appointments = db.Column(db.Integer, default=0)  # Agendamentos concluídos
    
    # Taxa de conversão (calculada)
    conversion_rate = db.Column(db.Float, default=0.0)  # % de visualizações que resultam em contato
    
    # Última atualização
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<ProfessionalMetrics {self.professional_id}>'
