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
from otp_service import create_otp, verify_otp, send_otp_email
from datetime import datetime

app = FastAPI(title="ISP Security System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── ZERO TRUST: Create all tables on startup ─────────────────────
models.Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {
        "message": "ISP Security System is running!",
        "principle": "Zero Trust Architecture — Never trust, always verify"
    }

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

    # ─── ZERO TRUST Step 1: Get context ──────────────────────────
    ip = request.client.host
    location_data = get_location_from_ip(ip)
    country = location_data["country"]
    city = location_data["city"]
    location = f"{city}, {country}"

    # ─── ZERO TRUST Step 2: Verify identity ──────────────────────
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
            ip=ip, location=location,
            device="Browser", success=False,
            risk_score=float(risk_score),
            action="blocked",
            explanation=explanation
        )
        return {
            "error": "Wrong password - login blocked",
            "risk_score": risk_score,
            "explanation": explanation
        }

    # ─── ZERO TRUST Step 3: Analyse behaviour ────────────────────
    failed_attempts = db.query(models.LoginEvent).filter(
        models.LoginEvent.username == username,
        models.LoginEvent.success == False
    ).count()

    risk_score, explanation = calculate_risk_score(
        hour=datetime.now().hour,
        country=country,
        failed_attempts=failed_attempts,
        is_new_device=0
    )

    # ─── ZERO TRUST Step 4: Decide action ────────────────────────
    action = decide_action(risk_score)

    # ─── ZERO TRUST Step 5: Execute response ─────────────────────
    if action == "otp":
        # Generate and send OTP
        otp_code = create_otp(db, username, user.email)
        success, msg = send_otp_email(user.email, username, otp_code)

        auth.save_login_event(
            db, username,
            ip=ip, location=location,
            device="Browser", success=False,
            risk_score=float(risk_score),
            action="otp",
            explanation=explanation
        )
        return {
            "message": "Suspicious activity detected — OTP sent to your email",
            "action": "otp",
            "risk_score": risk_score,
            "explanation": explanation,
            "otp_sent": msg
        }

    auth.save_login_event(
        db, username,
        ip=ip, location=location,
        device="Browser", success=True,
        risk_score=float(risk_score),
        action=action,
        explanation=explanation
    )

    if action == "allow":
        return {
            "message": f"Welcome {username}!",
            "risk_score": risk_score,
            "action": action,
            "location": location,
            "explanation": explanation
        }
    elif action == "restrict":
        return {
            "message": "Account restricted — suspicious activity detected",
            "risk_score": risk_score,
            "action": action,
            "explanation": explanation
        }
    else:
        return {
            "message": "Access blocked — critical risk detected",
            "risk_score": risk_score,
            "action": action,
            "explanation": explanation
        }

@app.post("/verify-otp")
def verify_otp_endpoint(username: str, otp_code: str,
                         db: Session = Depends(get_db)):
    success, message = verify_otp(db, username, otp_code)
    if success:
        return {
            "message": f"Welcome {username}! OTP verified successfully",
            "action": "allow",
            "verified": True
        }
    return {"error": message, "verified": False}

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