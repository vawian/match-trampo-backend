from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from models import db, Professional, Subscription, Schedule
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

