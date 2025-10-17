from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from models import db, Professional, Subscription, Schedule # Importa o DB e os modelos

app = Flask(__name__)
CORS(app) # Habilita CORS para permitir comunicação com o frontend React

# Configuração do Banco de Dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///match_trampo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# --- Funções de Lógica de Negócio (Refatoradas para usar o DB) ---

def block_time_slot_db(professional_id: str, start_time: datetime):
    """
    Bloqueia um slot de 2 horas usando o DB (RF 2.5).
    """
    end_time = start_time + timedelta(hours=2)
    
    # Verifica se o profissional existe
    professional = Professional.query.get(professional_id)
    if not professional:
        return {"status": "error", "message": "Profissional não encontrado."}
        
    # Cria o novo agendamento (bloqueio)
    new_schedule = Schedule(
        professional_id=professional_id,
        start_time=start_time,
        end_time=end_time,
        status='BLOCKED'
    )
    db.session.add(new_schedule)
    db.session.commit()
    
    return {"status": "success", "message": f"Slot bloqueado para {professional_id} das {start_time.strftime('%H:%M')} às {end_time.strftime('%H:%M')}"}

def release_block_db(professional_id: str, start_time_str: str):
    """
    Libera o bloqueio usando o DB ("Visita Encerrada" - RF 2.8.3).
    """
    try:
        start_time = datetime.fromisoformat(start_time_str)
    except ValueError:
        return {"status": "error", "message": "Formato de data/hora inválido."}

    schedule_item = Schedule.query.filter_by(
        professional_id=professional_id,
        start_time=start_time,
        status='BLOCKED'
    ).first()

    if schedule_item:
        schedule_item.status = 'RELEASED'
        db.session.commit()
        return {"status": "success", "message": f"Bloqueio liberado para {professional_id} a partir de {start_time_str}"}
    
    return {"status": "error", "message": "Bloqueio não encontrado ou já liberado."}

def get_professional_schedule_db(professional_id: str):
    """
    Retorna a agenda do profissional usando o DB.
    """
    schedules = Schedule.query.filter_by(professional_id=professional_id).all()
    return [{
        "start": item.start_time.isoformat(),
        "end": item.end_time.isoformat(),
        "status": item.status
    } for item in schedules]

def check_subscription_status_db(professional_id: str):
    """
    Verifica o status da assinatura de um profissional usando o DB (RF 2.9).
    """
    subscription = Subscription.query.filter_by(professional_id=professional_id).first()
    
    if not subscription:
        return {"status": "error", "message": "Profissional não encontrado ou sem assinatura."}
    
    is_active = subscription.status == "active"
    
    return {
        "professional_id": professional_id,
        "plan": subscription.plan,
        "status": subscription.status,
        "is_active": is_active,
        "message": "Assinatura ativa." if is_active else "Assinatura inativa. Acesso bloqueado (Inadimplência)."
    }

def process_payment_db(professional_id: str, amount: float):
    """
    Simula o processamento de um pagamento recorrente usando o DB.
    """
    subscription = Subscription.query.filter_by(professional_id=professional_id).first()
    
    if subscription:
        subscription.status = "active"
        # Simula a atualização da data de vencimento (apenas para fins de teste)
        subscription.due_date = datetime.now().date() + timedelta(days=30) 
        db.session.commit()
        return {"status": "success", "message": f"Pagamento de R$ {amount:.2f} processado com sucesso. Assinatura reativada."}
    
    return {"status": "error", "message": "Profissional não encontrado para processar pagamento."}

# --- Atualiza os endpoints para usar as novas funções ---

@app.route('/api/schedule/<professional_id>', methods=['GET'])
def get_schedule(professional_id):
    """Retorna a agenda do profissional."""
    schedule = get_professional_schedule_db(professional_id)
    return jsonify({"professional_id": professional_id, "schedule": schedule})

@app.route('/api/schedule/block', methods=['POST'])
def block_slot():
    """Bloqueia um slot de 2 horas para um profissional."""
    data = request.json
    professional_id = data.get('professional_id')
    start_time_str = data.get('start_time')
    
    if not professional_id or not start_time_str:
        return jsonify({"status": "error", "message": "Dados incompletos: professional_id e start_time são necessários."}), 400
        
    try:
        start_time = datetime.fromisoformat(start_time_str)
        result = block_time_slot_db(professional_id, start_time)
        return jsonify(result)
    except ValueError:
        return jsonify({"status": "error", "message": "Formato de data/hora inválido. Use o formato ISO 8601."}), 400

@app.route('/api/schedule/release', methods=['POST'])
def release_slot():
    """Libera o bloqueio de um slot ("Visita Encerrada")."""
    data = request.json
    professional_id = data.get('professional_id')
    start_time_str = data.get('start_time')
    
    if not professional_id or not start_time_str:
        return jsonify({"status": "error", "message": "Dados incompletos: professional_id e start_time são necessários."}), 400
        
    result = release_block_db(professional_id, start_time_str)
    return jsonify(result)

@app.route('/api/payment/subscription/<professional_id>', methods=['GET'])
def get_subscription(professional_id):
    """Verifica o status da assinatura do profissional (Bloqueio por Inadimplência)."""
    result = check_subscription_status_db(professional_id)
    if result["status"] == "error":
        return jsonify(result), 404
    return jsonify(result)

@app.route('/api/payment/process', methods=['POST'])
def process_payment_api():
    """Simula o processamento de pagamento."""
    data = request.json
    professional_id = data.get('professional_id')
    amount = data.get('amount')
    
    if not professional_id or not amount:
        return jsonify({"status": "error", "message": "Dados incompletos: professional_id e amount são necessários."}), 400
        
    try:
        amount = float(amount)
        result = process_payment_db(professional_id, amount)
        return jsonify(result)
    except ValueError:
        return jsonify({"status": "error", "message": "Valor do pagamento inválido."}), 400

# --- Endpoint de Busca e Ranqueamento (RF 2.3.2) ---

@app.route('/api/search/professionals', methods=['GET'])
def search_professionals():
    """
    Realiza a busca de profissionais com ranqueamento misto (Avaliação e Distância).
    Parâmetros: profession (string), city (string, opcional), state (string, opcional).
    """
    profession_query = request.args.get('profession')
    city_query = request.args.get('city')
    state_query = request.args.get('state')
    
    if not profession_query:
        return jsonify({"status": "error", "message": "O parâmetro 'profession' é obrigatório."}), 400

    # 1. Filtra por profissão
    # Usa ilike para busca case-insensitive
    query = db.session.query(Professional, Subscription.plan).join(Subscription, Professional.id == Subscription.professional_id)
    query = query.filter(Professional.profession.ilike(f'%{profession_query}%'))

    # 2. Filtra por localização (se fornecida)
    if city_query:
        query = query.filter(Professional.city.ilike(f'%{city_query}%'))
    if state_query:
        query = query.filter(Professional.state.ilike(f'%{state_query}%'))

    # 3. Ranqueamento Misto (RF 2.3.2): Prioriza Avaliação e Distância (Cidade/Estado)
    # A ordenação de prioridade será: Master > Rating > Proximidade (implícita pelo filtro)
    
    # Recupera todos os profissionais filtrados
    professionals_with_subscription = query.all()
    
    # Converte para um formato mais fácil de manipular e aplica a ordenação em Python
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
            "plan": plan,
            "is_master": plan == 'Master'
        })
        
    # Ordenação Final (Python): Master (True) > Rating (Decrescente)
    # O ranqueamento misto é aplicado aqui: Master (Prioridade) e Rating (Qualidade)
    results.sort(key=lambda x: (x['is_master'], x['rating']), reverse=True)

    return jsonify({"status": "success", "results": results})

# --- Função de Inicialização do DB ---

def init_db():
    with app.app_context():
        db.create_all()
        
        # 1. Cria profissionais de teste
        prof_123 = Professional(id='prof_123', name='João da Silva', profession='Eletricista', city='São Paulo', state='SP', rating=4.8, reviews=154)
        prof_789 = Professional(id='prof_789', name='Maria Souza', profession='Pintora', city='São Paulo', state='SP', rating=4.9, reviews=88)
        prof_456 = Professional(id='prof_456', name='Carlos Alberto', profession='Eletricista', city='Campinas', state='SP', rating=4.5, reviews=50)
        prof_101 = Professional(id='prof_101', name='Fernanda Costa', profession='Pintora', city='Rio de Janeiro', state='RJ', rating=5.0, reviews=200)
        
        db.session.add_all([prof_123, prof_789, prof_456, prof_101])
        db.session.commit()
        
        # 2. Cria assinaturas de teste
        sub_123 = Subscription(professional_id='prof_123', plan='Master', status='active', due_date=datetime.strptime('2025-11-15', '%Y-%m-%d').date())
        sub_789 = Subscription(professional_id='prof_789', plan='Profissional', status='inactive_inadimplencia', due_date=datetime.strptime('2025-09-01', '%Y-%m-%d').date())
        
        db.session.add_all([sub_123, sub_789])
        db.session.commit()
        
        print("Banco de dados inicializado e populado com dados de teste.")

if __name__ == '__main__':
    # Inicializa o DB antes de rodar o app
    init_db()
    app.run(host='0.0.0.0', port=5000)

@app.route('/api/status', methods=['GET'])
def status():
    """Endpoint simples para verificar se a API está online."""
    return jsonify({"status": "ok", "service": "Match Trampo Backend API"})

# --- Endpoints de Agendamento (RF 2.5, RF 2.8.3) ---

@app.route('/api/schedule/<professional_id>', methods=['GET'])
def get_schedule(professional_id):
    """Retorna a agenda do profissional."""
    schedule = get_professional_schedule(professional_id)
    return jsonify({"professional_id": professional_id, "schedule": schedule})

@app.route('/api/schedule/block', methods=['POST'])
def block_slot():
    """Bloqueia um slot de 2 horas para um profissional."""
    data = request.json
    professional_id = data.get('professional_id')
    start_time_str = data.get('start_time') # Espera string ISO 8601
    
    if not professional_id or not start_time_str:
        return jsonify({"status": "error", "message": "Dados incompletos: professional_id e start_time são necessários."}), 400
        
    try:
        # A lógica de agendamento espera um objeto datetime
        start_time = datetime.fromisoformat(start_time_str)
        result = block_time_slot(professional_id, start_time)
        return jsonify(result)
    except ValueError:
        return jsonify({"status": "error", "message": "Formato de data/hora inválido. Use o formato ISO 8601."}), 400

@app.route('/api/schedule/release', methods=['POST'])
def release_slot():
    """Libera o bloqueio de um slot ("Visita Encerrada")."""
    data = request.json
    professional_id = data.get('professional_id')
    start_time_str = data.get('start_time')
    
    if not professional_id or not start_time_str:
        return jsonify({"status": "error", "message": "Dados incompletos: professional_id e start_time são necessários."}), 400
        
    result = release_block(professional_id, start_time_str)
    return jsonify(result)

# --- Endpoints de Pagamento/Assinatura (RF 2.9) ---

@app.route('/api/payment/subscription/<professional_id>', methods=['GET'])
def get_subscription(professional_id):
    """Verifica o status da assinatura do profissional (Bloqueio por Inadimplência)."""
    result = check_subscription_status(professional_id)
    if result["status"] == "error":
        return jsonify(result), 404
    return jsonify(result)

@app.route('/api/payment/process', methods=['POST'])
def process_payment_api():
    """Simula o processamento de pagamento."""
    data = request.json
    professional_id = data.get('professional_id')
    amount = data.get('amount')
    
    if not professional_id or not amount:
        return jsonify({"status": "error", "message": "Dados incompletos: professional_id e amount são necessários."}), 400
        
    try:
        amount = float(amount)
        result = process_payment(professional_id, amount)
        return jsonify(result)
    except ValueError:
        return jsonify({"status": "error", "message": "Valor do pagamento inválido."}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

