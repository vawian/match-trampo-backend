"""
Script para popular o banco de dados com dados de teste de chat
"""
from app import app
from models import db, Chat, Message
from datetime import datetime, timedelta

def seed_chat_data():
    with app.app_context():
        # Limpar dados de chat existentes
        Message.query.delete()
        Chat.query.delete()
        db.session.commit()
        
        # Criar chats de teste com localização
        chat1 = Chat(
            client_id="client_001",
            professional_id="prof_123",
            created_at=datetime.utcnow() - timedelta(days=2),
            last_message_at=datetime.utcnow() - timedelta(hours=1),
            client_latitude=-23.5629,  # Região da Av. Paulista, São Paulo
            client_longitude=-46.6544,
            client_address="Av. Paulista, 1578 - Bela Vista, São Paulo - SP"
        )
        
        chat2 = Chat(
            client_id="client_001",
            professional_id="prof_789",
            created_at=datetime.utcnow() - timedelta(days=1),
            last_message_at=datetime.utcnow() - timedelta(minutes=30),
            client_latitude=-23.5475,  # Região do Parque Ibirapuera, São Paulo
            client_longitude=-46.6361,
            client_address="Av. Pedro Álvares Cabral - Vila Mariana, São Paulo - SP"
        )
        
        chat3 = Chat(
            client_id="client_001",
            professional_id="prof_202",
            created_at=datetime.utcnow() - timedelta(hours=5),
            last_message_at=datetime.utcnow() - timedelta(minutes=5),
            client_latitude=-23.5489,  # Região da Liberdade, São Paulo
            client_longitude=-46.6388,
            client_address="Rua Galvão Bueno, 209 - Liberdade, São Paulo - SP"
        )
        
        db.session.add_all([chat1, chat2, chat3])
        db.session.commit()
        
        # Criar mensagens de teste para chat1 (João da Silva - Eletricista)
        messages_chat1 = [
            Message(
                chat_id=chat1.id,
                sender_id="client_001",
                sender_type="client",
                content="Olá João! Preciso de um orçamento para instalação de pontos de tomada.",
                sent_at=datetime.utcnow() - timedelta(days=2),
                is_read=True
            ),
            Message(
                chat_id=chat1.id,
                sender_id="prof_123",
                sender_type="professional",
                content="Olá! Claro, posso te ajudar. Quantos pontos você precisa instalar?",
                sent_at=datetime.utcnow() - timedelta(days=2) + timedelta(minutes=15),
                is_read=True
            ),
            Message(
                chat_id=chat1.id,
                sender_id="client_001",
                sender_type="client",
                content="Preciso de 5 pontos na sala e 3 no quarto.",
                sent_at=datetime.utcnow() - timedelta(days=2) + timedelta(minutes=20),
                is_read=True
            ),
            Message(
                chat_id=chat1.id,
                sender_id="prof_123",
                sender_type="professional",
                content="Entendi. Posso fazer uma visita técnica amanhã às 14h para avaliar melhor. Pode ser?",
                sent_at=datetime.utcnow() - timedelta(hours=1),
                is_read=False
            ),
        ]
        
        # Criar mensagens de teste para chat2 (Maria Souza - Pintora)
        messages_chat2 = [
            Message(
                chat_id=chat2.id,
                sender_id="client_001",
                sender_type="client",
                content="Oi Maria! Gostaria de um orçamento para pintura de apartamento.",
                sent_at=datetime.utcnow() - timedelta(days=1),
                is_read=True
            ),
            Message(
                chat_id=chat2.id,
                sender_id="prof_789",
                sender_type="professional",
                content="Oi! Qual o tamanho do apartamento?",
                sent_at=datetime.utcnow() - timedelta(days=1) + timedelta(hours=2),
                is_read=True
            ),
            Message(
                chat_id=chat2.id,
                sender_id="client_001",
                sender_type="client",
                content="São 80m², 2 quartos, sala e cozinha.",
                sent_at=datetime.utcnow() - timedelta(days=1) + timedelta(hours=2, minutes=10),
                is_read=True
            ),
            Message(
                chat_id=chat2.id,
                sender_id="prof_789",
                sender_type="professional",
                content="Perfeito! Para esse tamanho, o valor fica em torno de R$ 2.500,00 com material incluso. Posso agendar uma visita para confirmar?",
                sent_at=datetime.utcnow() - timedelta(minutes=30),
                is_read=False
            ),
        ]
        
        # Criar mensagens de teste para chat3 (Pedro Santos - Encanador)
        messages_chat3 = [
            Message(
                chat_id=chat3.id,
                sender_id="client_001",
                sender_type="client",
                content="Pedro, estou com um vazamento no banheiro. Pode me atender hoje?",
                sent_at=datetime.utcnow() - timedelta(hours=5),
                is_read=True
            ),
            Message(
                chat_id=chat3.id,
                sender_id="prof_202",
                sender_type="professional",
                content="Olá! Sim, posso ir aí. Qual o endereço?",
                sent_at=datetime.utcnow() - timedelta(hours=4, minutes=50),
                is_read=True
            ),
            Message(
                chat_id=chat3.id,
                sender_id="client_001",
                sender_type="client",
                content="Rua Galvão Bueno, 209 - Liberdade",
                sent_at=datetime.utcnow() - timedelta(hours=4, minutes=45),
                is_read=True
            ),
            Message(
                chat_id=chat3.id,
                sender_id="prof_202",
                sender_type="professional",
                content="Perfeito! Estou saindo agora e chego aí em uns 40 minutos.",
                sent_at=datetime.utcnow() - timedelta(hours=4, minutes=40),
                is_read=True
            ),
            Message(
                chat_id=chat3.id,
                sender_id="client_001",
                sender_type="client",
                content="Ótimo! Te espero aqui.",
                sent_at=datetime.utcnow() - timedelta(hours=4, minutes=35),
                is_read=True
            ),
            Message(
                chat_id=chat3.id,
                sender_id="prof_202",
                sender_type="professional",
                content="Cheguei! Estou na portaria.",
                sent_at=datetime.utcnow() - timedelta(minutes=5),
                is_read=False
            ),
        ]
        
        db.session.add_all(messages_chat1 + messages_chat2 + messages_chat3)
        db.session.commit()
        
        print("✅ Dados de chat populados com sucesso!")
        print(f"   - {len([chat1, chat2, chat3])} chats criados")
        print(f"   - {len(messages_chat1 + messages_chat2 + messages_chat3)} mensagens criadas")
        print("   - Todos os chats incluem localização do cliente")

if __name__ == "__main__":
    seed_chat_data()

