from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from logic.scheduling import block_time_slot, release_block, get_professional_schedule
from logic.payment import check_subscription_status, process_payment

app = Flask(__name__)
CORS(app) # Habilita CORS para permitir comunicação com o frontend React

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

