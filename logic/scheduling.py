import datetime

# Dicionário para simular um banco de dados de agendamentos e bloqueios
# Chave: ID do Profissional, Valor: Lista de slots bloqueados (datetime objects)
PROFESSIONAL_SCHEDULES = {}

def block_time_slot(professional_id: str, start_time: datetime.datetime):
    """
    Simula o bloqueio de um slot de 2 horas para um profissional (RF 2.5).
    """
    end_time = start_time + datetime.timedelta(hours=2)
    
    if professional_id not in PROFESSIONAL_SCHEDULES:
        PROFESSIONAL_SCHEDULES[professional_id] = []
        
    # Simplesmente adiciona o slot bloqueado (para fins de simulação)
    PROFESSIONAL_SCHEDULES[professional_id].append({
        "start": start_time.isoformat(),
        "end": end_time.isoformat(),
        "status": "BLOCKED"
    })
    
    return {"status": "success", "message": f"Slot bloqueado para {professional_id} das {start_time.strftime('%H:%M')} às {end_time.strftime('%H:%M')}"}

def release_block(professional_id: str, start_time_str: str):
    """
    Simula o botão "Visita Encerrada" (RF 2.8.3), liberando o bloqueio.
    Para simplificar, remove o bloqueio mais recente que corresponde ao start_time.
    """
    if professional_id in PROFESSIONAL_SCHEDULES:
        # Converte a string de volta para datetime para comparação
        start_time_to_match = datetime.datetime.fromisoformat(start_time_str)
        
        for slot in PROFESSIONAL_SCHEDULES[professional_id]:
            if slot["start"] == start_time_to_match.isoformat() and slot["status"] == "BLOCKED":
                slot["status"] = "RELEASED" # Marca como liberado em vez de remover
                return {"status": "success", "message": f"Bloqueio liberado para {professional_id} a partir de {start_time_str}"}
                
    return {"status": "error", "message": "Bloqueio não encontrado ou já liberado."}

def get_professional_schedule(professional_id: str):
    """
    Retorna a agenda do profissional.
    """
    return PROFESSIONAL_SCHEDULES.get(professional_id, [])

# Simulação de dados iniciais
# PROFESSIONAL_SCHEDULES["prof_123"] = [
#     {"start": "2025-10-17T10:00:00", "end": "2025-10-17T12:00:00", "status": "BLOCKED"}
# ]

