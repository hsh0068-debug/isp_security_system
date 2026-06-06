import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ml_model'))

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, get_db
import models
import auth
from risk_scorer import calculate_risk_score, decide_action
from geolocation import get_location_from_ip
from datetime import datetime

app = FastAPI(title="ISP Security System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "ISP Security System is running!"}

@app.post("/register")
def register(username: str, password: str, email: str,
             db: Session = Depends(get_db)):
    existing = auth.get_user(db, username)
    if existing:
        return {"error": "Username already exists"}
    user = auth.create_user(db, username, password, email)
    return {"message": f"User {username} created successfully!"}

@app.post("/login")
def login(username: str, password: str, request: Request,
          db: Session = Depends(get_db)):

    ip = request.client.host
    location_data = get_location_from_ip(ip)
    country = location_data["country"]
    city = location_data["city"]
    location = f"{city}, {country}"

    user = auth.get_user(db, username)
    if not user:
        return {"error": "User not found"}

    if not auth.verify_password(password, user.password_hash):
        failed = db.query(models.LoginEvent).filter(
            models.LoginEvent.username == username,
            models.LoginEvent.success == False
        ).count()

        risk_score, explanation = calculate_risk_score(
            hour=datetime.now().hour,
            country=country,
            failed_attempts=failed + 1,
            is_new_device=1
        )

        auth.save_login_event(
            db, username,
            ip=ip,
            location=location,
            device="Browser",
            success=False,
            risk_score=float(risk_score),
            action="blocked",
            explanation=explanation
        )
        return {
            "error": "Wrong password - login blocked",
            "risk_score": risk_score,
            "explanation": explanation
        }

    failed_attempts = db.query(models.LoginEvent).filter(
        models.LoginEvent.username == username,
        models.LoginEvent.success == False
    ).count()

    current_hour = datetime.now().hour

    risk_score, explanation = calculate_risk_score(
        hour=current_hour,
        country=country,
        failed_attempts=failed_attempts,
        is_new_device=0
    )

    action = decide_action(risk_score)

    auth.save_login_event(
        db, username,
        ip=ip,
        location=location,
        device="Browser",
        success=True,
        risk_score=float(risk_score),
        action=action,
        explanation=explanation
    )

    return {
        "message": f"Welcome {username}!",
        "risk_score": risk_score,
        "action": action,
        "location": location,
        "explanation": explanation
    }

@app.get("/login-events")
def get_login_events(db: Session = Depends(get_db)):
    events = db.query(models.LoginEvent).all()
    return events

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(models.LoginEvent).count()
    blocked = db.query(models.LoginEvent).filter(
        models.LoginEvent.action_taken == "blocked"
    ).count()
    safe = db.query(models.LoginEvent).filter(
        models.LoginEvent.action_taken == "allow"
    ).count()
    high_risk = db.query(models.LoginEvent).filter(
        models.LoginEvent.risk_score > 60
    ).count()
    otp = db.query(models.LoginEvent).filter(
        models.LoginEvent.action_taken == "otp"
    ).count()
    return {
        "total": total,
        "blocked": blocked,
        "safe": safe,
        "high_risk": high_risk,
        "otp": otp
    }