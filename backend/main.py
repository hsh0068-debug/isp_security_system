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
    user = auth.get_user(db, username)
    if not user:
        return {"error": "User not found"}

    if not auth.verify_password(password, user.password_hash):
        auth.save_login_event(
            db, username,
            ip=request.client.host,
            location="Unknown",
            device="Browser",
            success=False,
            risk_score=80.0,
            action="blocked"
        )
        return {"error": "Wrong password - login blocked"}

    current_hour = datetime.now().hour

    risk_score = calculate_risk_score(
        hour=current_hour,
        country="Sri Lanka",
        failed_attempts=0,
        is_new_device=0
    )

    action = decide_action(risk_score)

    auth.save_login_event(
        db, username,
        ip=request.client.host,
        location="Colombo",
        device="Browser",
        success=True,
        risk_score=float(risk_score),
        action=action
    )

    if action == "allow":
        return {"message": f"Welcome {username}!", "risk_score": risk_score, "action": action}
    elif action == "otp":
        return {"message": "OTP verification required", "risk_score": risk_score, "action": action}
    elif action == "restrict":
        return {"message": "Account restricted - suspicious activity", "risk_score": risk_score, "action": action}
    else:
        return {"message": "Access blocked - high risk detected", "risk_score": risk_score, "action": action}

@app.get("/login-events")
def get_login_events(db: Session = Depends(get_db)):
    events = db.query(models.LoginEvent).all()
    return events