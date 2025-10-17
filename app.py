from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from models import db, Professional, Subscription, Schedule, Chat, Message, ProfessionalMetrics
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///match_trampo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Raio da Terra em quilômetros
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

@app.route("/api/search/professionals", methods=["GET"])
def search_professionals():
    profession_query = request.args.get("profession")
    city_query = request.args.get("city")
    state_query = request.args.get("state")
    user_latitude = request.args.get("latitude", type=float)
    user_longitude = request.args.get("longitude", type=float)

    if not profession_query:
        return jsonify({"status": "error", "message": "O parâmetro 'profession' é obrigatório."}), 400

    query = db.session.query(Professional, Subscription.plan).join(Subscription, Professional.id == Subscription.professional_id)
    query = query.filter(Professional.profession.ilike(f"%{profession_query}%"))

    if city_query:
        query = query.filter(Professional.city.ilike(f"%{city_query}%"))
    if state_query:
        query = query.filter(Professional.state.ilike(f"%{state_query}%"))

    if user_latitude is not None and user_longitude is not None:
        query = query.filter(Professional.latitude.isnot(None), Professional.longitude.isnot(None))

    professionals_with_subscription = query.all()

    results = []
    for professional, plan in professionals_with_subscription:
        results.append({
            "id": professional.id,
            "name": professional.name,
            "profession": professional.profession,
            "city": professional.city,
            "state": professional.state,
            "rating": professional.rating,
            "reviews": professional.reviews,
            "latitude": professional.latitude,
            "longitude": professional.longitude,
            "plan": plan,
            "is_master": plan == "Master",
            "distance": None
        })

    if user_latitude is not None and user_longitude is not None:
        for prof in results:
            if prof["latitude"] is not None and prof["longitude"] is not None:
                prof["distance"] = haversine(user_latitude, user_longitude, prof["latitude"], prof["longitude"])
        results.sort(key=lambda x: (x["is_master"], x["rating"], x["distance"] if x["distance"] is not None else float("inf")), reverse=True)
    else:
        results.sort(key=lambda x: (x["is_master"], x["rating"]), reverse=True)

    return jsonify({"status": "success", "results": results})

@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({"status": "ok", "service": "Match Trampo Backend API"})

# ==================== ENDPOINTS DE CHAT ====================

@app.route("/api/chats", methods=["GET"])
def get_chats():
    """Retorna todos os chats de um usuário (cliente ou profissional)"""
    user_id = request.args.get("user_id")
    user_type = request.args.get("user_type")  # 'client' ou 'professional'
    
    if not user_id or not user_type:
        return jsonify({"status": "error", "message": "user_id e user_type são obrigatórios."}), 400
    
    if user_type == "client":
        chats = Chat.query.filter_by(client_id=user_id).order_by(Chat.last_message_at.desc()).all()
    elif user_type == "professional":
        chats = Chat.query.filter_by(professional_id=user_id).order_by(Chat.last_message_at.desc()).all()
    else:
        return jsonify({"status": "error", "message": "user_type deve ser 'client' ou 'professional'."}), 400
    
    result = []
    for chat in chats:
        last_message = chat.messages.order_by(Message.sent_at.desc()).first()
        unread_count = chat.messages.filter_by(is_read=False).filter(Message.sender_id != user_id).count()
        
        result.append({
            "id": chat.id,
            "client_id": chat.client_id,
            "professional_id": chat.professional_id,
            "professional_name": chat.professional.name,
            "professional_profession": chat.professional.profession,
            "last_message": last_message.content if last_message else None,
            "last_message_at": last_message.sent_at.isoformat() if last_message else chat.created_at.isoformat(),
            "unread_count": unread_count,
            "client_latitude": chat.client_latitude,
            "client_longitude": chat.client_longitude,
            "client_address": chat.client_address
        })
    
    return jsonify({"status": "success", "chats": result})

@app.route("/api/chats/<int:chat_id>/messages", methods=["GET"])
def get_messages(chat_id):
    """Retorna todas as mensagens de um chat específico"""
    chat = Chat.query.get(chat_id)
    
    if not chat:
        return jsonify({"status": "error", "message": "Chat não encontrado."}), 404
    
    messages = chat.messages.all()
    
    result = []
    for msg in messages:
        result.append({
            "id": msg.id,
            "sender_id": msg.sender_id,
            "sender_type": msg.sender_type,
            "content": msg.content,
            "sent_at": msg.sent_at.isoformat(),
            "is_read": msg.is_read
        })
    
    return jsonify({"status": "success", "messages": result})

@app.route("/api/chats", methods=["POST"])
def create_or_get_chat():
    """Cria um novo chat ou retorna um existente entre cliente e profissional"""
    data = request.get_json()
    client_id = data.get("client_id")
    professional_id = data.get("professional_id")
    client_latitude = data.get("client_latitude")
    client_longitude = data.get("client_longitude")
    client_address = data.get("client_address")
    
    if not client_id or not professional_id:
        return jsonify({"status": "error", "message": "client_id e professional_id são obrigatórios."}), 400
    
    # Verifica se já existe um chat entre esses usuários
    existing_chat = Chat.query.filter_by(client_id=client_id, professional_id=professional_id).first()
    
    if existing_chat:
        # Atualizar localização se fornecida
        if client_latitude is not None and client_longitude is not None:
            existing_chat.client_latitude = client_latitude
            existing_chat.client_longitude = client_longitude
            existing_chat.client_address = client_address
            db.session.commit()
        return jsonify({"status": "success", "chat_id": existing_chat.id, "created": False})
    
    # Cria um novo chat
    new_chat = Chat(
        client_id=client_id,
        professional_id=professional_id,
        client_latitude=client_latitude,
        client_longitude=client_longitude,
        client_address=client_address
    )
    db.session.add(new_chat)
    db.session.commit()
    
    return jsonify({"status": "success", "chat_id": new_chat.id, "created": True}), 201

@app.route("/api/chats/<int:chat_id>/messages", methods=["POST"])
def send_message(chat_id):
    """Envia uma nova mensagem em um chat"""
    chat = Chat.query.get(chat_id)
    
    if not chat:
        return jsonify({"status": "error", "message": "Chat não encontrado."}), 404
    
    data = request.get_json()
    sender_id = data.get("sender_id")
    sender_type = data.get("sender_type")  # 'client' ou 'professional'
    content = data.get("content")
    
    if not sender_id or not sender_type or not content:
        return jsonify({"status": "error", "message": "sender_id, sender_type e content são obrigatórios."}), 400
    
    if sender_type not in ["client", "professional"]:
        return jsonify({"status": "error", "message": "sender_type deve ser 'client' ou 'professional'."}), 400
    
    # Cria a nova mensagem
    new_message = Message(
        chat_id=chat_id,
        sender_id=sender_id,
        sender_type=sender_type,
        content=content
    )
    
    # Atualiza o timestamp do último mensagem no chat
    chat.last_message_at = datetime.utcnow()
    
    db.session.add(new_message)
    db.session.commit()
    
    return jsonify({
        "status": "success",
        "message": {
            "id": new_message.id,
            "sender_id": new_message.sender_id,
            "sender_type": new_message.sender_type,
            "content": new_message.content,
            "sent_at": new_message.sent_at.isoformat(),
            "is_read": new_message.is_read
        }
    }), 201

@app.route("/api/chats/<int:chat_id>/messages/<int:message_id>/read", methods=["PUT"])
def mark_message_as_read(chat_id, message_id):
    """Marca uma mensagem como lida"""
    message = Message.query.filter_by(id=message_id, chat_id=chat_id).first()
    
    if not message:
        return jsonify({"status": "error", "message": "Mensagem não encontrada."}), 404
    
    message.is_read = True
    db.session.commit()
    
    return jsonify({"status": "success", "message": "Mensagem marcada como lida."})

@app.route("/api/chats/<int:chat_id>/messages/read-all", methods=["PUT"])
def mark_all_messages_as_read(chat_id):
    """Marca todas as mensagens de um chat como lidas para um usuário específico"""
    data = request.get_json()
    user_id = data.get("user_id")
    
    if not user_id:
        return jsonify({"status": "error", "message": "user_id é obrigatório."}), 400
    
    chat = Chat.query.get(chat_id)
    if not chat:
        return jsonify({"status": "error", "message": "Chat não encontrado."}), 404
    
    # Marca como lidas todas as mensagens que não foram enviadas pelo usuário
    messages = chat.messages.filter(Message.sender_id != user_id, Message.is_read == False).all()
    
    for msg in messages:
        msg.is_read = True
    
    db.session.commit()
    
    return jsonify({"status": "success", "message": f"{len(messages)} mensagens marcadas como lidas."})

# ==================== FIM DOS ENDPOINTS DE CHAT ====================

# ==================== ENDPOINTS DO DASHBOARD ====================

@app.route("/api/professionals/<string:professional_id>/metrics", methods=["GET"])
def get_professional_metrics(professional_id):
    """Retorna as métricas de desempenho de um profissional"""
    professional = Professional.query.get(professional_id)
    
    if not professional:
        return jsonify({"status": "error", "message": "Profissional não encontrado."}), 404
    
    metrics = ProfessionalMetrics.query.filter_by(professional_id=professional_id).first()
    
    if not metrics:
        # Criar métricas padrão se não existirem
        metrics = ProfessionalMetrics(professional_id=professional_id)
        db.session.add(metrics)
        db.session.commit()
    
    # Calcular taxa de conversão
    if metrics.profile_views > 0:
        total_contacts = metrics.whatsapp_clicks + metrics.chat_conversations
        metrics.conversion_rate = (total_contacts / metrics.profile_views) * 100
    
    return jsonify({
        "status": "success",
        "metrics": {
            "profile_views": metrics.profile_views,
            "profile_views_this_month": metrics.profile_views_this_month,
            "whatsapp_clicks": metrics.whatsapp_clicks,
            "whatsapp_clicks_this_month": metrics.whatsapp_clicks_this_month,
            "chat_conversations": metrics.chat_conversations,
            "chat_conversations_this_month": metrics.chat_conversations_this_month,
            "total_appointments": metrics.total_appointments,
            "appointments_this_month": metrics.appointments_this_month,
            "completed_appointments": metrics.completed_appointments,
            "conversion_rate": round(metrics.conversion_rate, 2),
            "last_updated": metrics.last_updated.isoformat()
        }
    })

@app.route("/api/professionals/<string:professional_id>/dashboard", methods=["GET"])
def get_professional_dashboard(professional_id):
    """Retorna dados completos do dashboard do profissional"""
    professional = Professional.query.get(professional_id)
    
    if not professional:
        return jsonify({"status": "error", "message": "Profissional não encontrado."}), 404
    
    # Buscar métricas
    metrics = ProfessionalMetrics.query.filter_by(professional_id=professional_id).first()
    if not metrics:
        metrics = ProfessionalMetrics(professional_id=professional_id)
        db.session.add(metrics)
        db.session.commit()
    
    # Buscar assinatura
    subscription = Subscription.query.filter_by(professional_id=professional_id).first()
    
    # Buscar chats ativos
    active_chats = Chat.query.filter_by(professional_id=professional_id).count()
    
    # Buscar agendamentos futuros
    upcoming_schedules = Schedule.query.filter(
        Schedule.professional_id == professional_id,
        Schedule.start_time > datetime.utcnow(),
        Schedule.status == 'BLOCKED'
    ).order_by(Schedule.start_time).limit(5).all()
    
    schedules_data = []
    for schedule in upcoming_schedules:
        schedules_data.append({
            "id": schedule.id,
            "start_time": schedule.start_time.isoformat(),
            "end_time": schedule.end_time.isoformat(),
            "status": schedule.status
        })
    
    # Calcular taxa de conversão
    if metrics.profile_views > 0:
        total_contacts = metrics.whatsapp_clicks + metrics.chat_conversations
        conversion_rate = (total_contacts / metrics.profile_views) * 100
    else:
        conversion_rate = 0.0
    
    return jsonify({
        "status": "success",
        "dashboard": {
            "professional": {
                "id": professional.id,
                "name": professional.name,
                "profession": professional.profession,
                "city": professional.city,
                "state": professional.state,
                "rating": professional.rating,
                "reviews": professional.reviews
            },
            "subscription": {
                "plan": subscription.plan if subscription else "Nenhum",
                "status": subscription.status if subscription else "inactive",
                "due_date": subscription.due_date.isoformat() if subscription and subscription.due_date else None
            },
            "metrics": {
                "profile_views": metrics.profile_views,
                "profile_views_this_month": metrics.profile_views_this_month,
                "whatsapp_clicks": metrics.whatsapp_clicks,
                "whatsapp_clicks_this_month": metrics.whatsapp_clicks_this_month,
                "chat_conversations": metrics.chat_conversations,
                "chat_conversations_this_month": metrics.chat_conversations_this_month,
                "total_appointments": metrics.total_appointments,
                "appointments_this_month": metrics.appointments_this_month,
                "completed_appointments": metrics.completed_appointments,
                "conversion_rate": round(conversion_rate, 2)
            },
            "active_chats": active_chats,
            "upcoming_schedules": schedules_data
        }
    })

@app.route("/api/professionals/<string:professional_id>/metrics/increment", methods=["POST"])
def increment_metric(professional_id):
    """Incrementa uma métrica específica do profissional"""
    data = request.get_json()
    metric_name = data.get("metric")
    
    if not metric_name:
        return jsonify({"status": "error", "message": "O campo 'metric' é obrigatório."}), 400
    
    metrics = ProfessionalMetrics.query.filter_by(professional_id=professional_id).first()
    
    if not metrics:
        metrics = ProfessionalMetrics(professional_id=professional_id)
        db.session.add(metrics)
    
    # Incrementar a métrica especificada
    valid_metrics = [
        'profile_views', 'profile_views_this_month',
        'whatsapp_clicks', 'whatsapp_clicks_this_month',
        'chat_conversations', 'chat_conversations_this_month',
        'total_appointments', 'appointments_this_month',
        'completed_appointments'
    ]
    
    if metric_name not in valid_metrics:
        return jsonify({"status": "error", "message": f"Métrica '{metric_name}' inválida."}), 400
    
    current_value = getattr(metrics, metric_name)
    setattr(metrics, metric_name, current_value + 1)
    
    db.session.commit()
    
    return jsonify({"status": "success", "message": f"Métrica '{metric_name}' incrementada com sucesso."})

# ==================== FIM DOS ENDPOINTS DO DASHBOARD ====================

def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()

        prof_123 = Professional(id="prof_123", name="João da Silva", profession="Eletricista", city="São Paulo", state="SP", rating=4.8, reviews=154, latitude=-23.5505, longitude=-46.6333)
        prof_789 = Professional(id="prof_789", name="Maria Souza", profession="Pintora", city="São Paulo", state="SP", rating=4.9, reviews=88, latitude=-23.5505, longitude=-46.6333)
        prof_456 = Professional(id="prof_456", name="Carlos Alberto", profession="Eletricista", city="Campinas", state="SP", rating=4.5, reviews=50, latitude=-22.9099, longitude=-47.0626)
        prof_101 = Professional(id="prof_101", name="Fernanda Costa", profession="Pintora", city="Rio de Janeiro", state="RJ", rating=5.0, reviews=200, latitude=-22.9068, longitude=-43.1729)
        prof_202 = Professional(id="prof_202", name="Pedro Santos", profession="Encanador", city="São Paulo", state="SP", rating=4.7, reviews=75, latitude=-23.5613, longitude=-46.6560)
        prof_303 = Professional(id="prof_303", name="Ana Paula", profession="Eletricista", city="Belo Horizonte", state="MG", rating=4.6, reviews=60, latitude=-19.9167, longitude=-43.9345)

        db.session.add_all([prof_123, prof_789, prof_456, prof_101, prof_202, prof_303])
        db.session.commit()

        sub_123 = Subscription(professional_id="prof_123", plan="Master", status="active", due_date=datetime.strptime("2025-11-15", "%Y-%m-%d").date())
        sub_789 = Subscription(professional_id="prof_789", plan="Profissional", status="active", due_date=datetime.strptime("2025-09-01", "%Y-%m-%d").date())
        sub_456 = Subscription(professional_id="prof_456", plan="Profissional", status="active", due_date=datetime.strptime("2025-11-15", "%Y-%m-%d").date())
        sub_101 = Subscription(professional_id="prof_101", plan="Master", status="active", due_date=datetime.strptime("2025-11-15", "%Y-%m-%d").date())
        sub_202 = Subscription(professional_id="prof_202", plan="Profissional", status="active", due_date=datetime.strptime("2025-11-15", "%Y-%m-%d").date())
        sub_303 = Subscription(professional_id="prof_303", plan="Profissional", status="active", due_date=datetime.strptime("2025-11-15", "%Y-%m-%d").date())

        db.session.add_all([sub_123, sub_789, sub_456, sub_101, sub_202, sub_303])
        db.session.commit()

        print("Banco de dados inicializado e populado com dados de teste.")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)

