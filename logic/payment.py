# Dicionário para simular um banco de dados de assinaturas de profissionais
# Chave: ID do Profissional, Valor: Status da Assinatura
PROFESSIONAL_SUBSCRIPTIONS = {
    "prof_123": {"plan": "Master", "status": "active", "due_date": "2025-11-15"},
    "prof_456": {"plan": "Profissional", "status": "active", "due_date": "2025-10-20"},
    "prof_789": {"plan": "Profissional", "status": "inactive_inadimplencia", "due_date": "2025-09-01"}, # Exemplo de bloqueado
}

def check_subscription_status(professional_id: str):
    """
    Verifica o status da assinatura de um profissional.
    Simula o Bloqueio por Inadimplência (RF 2.9).
    """
    sub = PROFESSIONAL_SUBSCRIPTIONS.get(professional_id)
    if not sub:
        return {"status": "error", "message": "Profissional não encontrado."}
    
    is_active = sub["status"] == "active"
    
    return {
        "professional_id": professional_id,
        "plan": sub["plan"],
        "status": sub["status"],
        "is_active": is_active,
        "message": "Assinatura ativa." if is_active else "Assinatura inativa. Acesso bloqueado (Inadimplência)."
    }

def process_payment(professional_id: str, amount: float):
    """
    Simula o processamento de um pagamento recorrente.
    """
    # Lógica de simulação: se o pagamento for processado, o status volta a ser 'active'
    if professional_id in PROFESSIONAL_SUBSCRIPTIONS:
        PROFESSIONAL_SUBSCRIPTIONS[professional_id]["status"] = "active"
        PROFESSIONAL_SUBSCRIPTIONS[professional_id]["due_date"] = "2025-11-15" # Atualiza data de vencimento
        return {"status": "success", "message": f"Pagamento de R$ {amount:.2f} processado com sucesso. Assinatura reativada."}
    
    return {"status": "error", "message": "Profissional não encontrado para processar pagamento."}

