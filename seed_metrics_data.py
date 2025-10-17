"""
Script para popular o banco de dados com métricas de teste para os profissionais
"""
from app import app
from models import db, ProfessionalMetrics
from datetime import datetime

def seed_metrics_data():
    with app.app_context():
        # Limpar métricas existentes
        ProfessionalMetrics.query.delete()
        db.session.commit()
        
        # Criar métricas de teste para cada profissional
        metrics_data = [
            {
                'professional_id': 'prof_123',
                'profile_views': 450,
                'profile_views_this_month': 85,
                'whatsapp_clicks': 120,
                'whatsapp_clicks_this_month': 28,
                'chat_conversations': 95,
                'chat_conversations_this_month': 22,
                'total_appointments': 78,
                'appointments_this_month': 15,
                'completed_appointments': 72,
            },
            {
                'professional_id': 'prof_789',
                'profile_views': 320,
                'profile_views_this_month': 62,
                'whatsapp_clicks': 85,
                'whatsapp_clicks_this_month': 18,
                'chat_conversations': 68,
                'chat_conversations_this_month': 15,
                'total_appointments': 54,
                'appointments_this_month': 11,
                'completed_appointments': 50,
            },
            {
                'professional_id': 'prof_456',
                'profile_views': 280,
                'profile_views_this_month': 45,
                'whatsapp_clicks': 72,
                'whatsapp_clicks_this_month': 12,
                'chat_conversations': 55,
                'chat_conversations_this_month': 10,
                'total_appointments': 42,
                'appointments_this_month': 8,
                'completed_appointments': 38,
            },
            {
                'professional_id': 'prof_101',
                'profile_views': 580,
                'profile_views_this_month': 110,
                'whatsapp_clicks': 165,
                'whatsapp_clicks_this_month': 35,
                'chat_conversations': 125,
                'chat_conversations_this_month': 28,
                'total_appointments': 95,
                'appointments_this_month': 20,
                'completed_appointments': 90,
            },
            {
                'professional_id': 'prof_202',
                'profile_views': 390,
                'profile_views_this_month': 72,
                'whatsapp_clicks': 98,
                'whatsapp_clicks_this_month': 20,
                'chat_conversations': 82,
                'chat_conversations_this_month': 18,
                'total_appointments': 65,
                'appointments_this_month': 13,
                'completed_appointments': 60,
            },
            {
                'professional_id': 'prof_303',
                'profile_views': 310,
                'profile_views_this_month': 58,
                'whatsapp_clicks': 78,
                'whatsapp_clicks_this_month': 15,
                'chat_conversations': 62,
                'chat_conversations_this_month': 12,
                'total_appointments': 48,
                'appointments_this_month': 9,
                'completed_appointments': 44,
            },
        ]
        
        metrics_objects = []
        for data in metrics_data:
            metrics = ProfessionalMetrics(**data)
            metrics_objects.append(metrics)
        
        db.session.add_all(metrics_objects)
        db.session.commit()
        
        print("✅ Métricas de profissionais populadas com sucesso!")
        print(f"   - {len(metrics_objects)} conjuntos de métricas criados")

if __name__ == "__main__":
    seed_metrics_data()

