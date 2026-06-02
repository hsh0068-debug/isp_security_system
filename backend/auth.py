from sqlalchemy.orm import Session
from models import User, LoginEvent
from datetime import datetime
import hashlib

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str):
    return hash_password(plain_password) == hashed_password

def create_user(db: Session, username: str, password: str, email: str):
    hashed = hash_password(password)
    user = User(username=username, password_hash=hashed, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def save_login_event(db: Session, username: str, ip: str,
                     location: str, device: str, success: bool,
                     risk_score: float, action: str):
    event = LoginEvent(
        username=username,
        ip_address=ip,
        location=location,
        device_type=device,
        login_time=datetime.now(),
        success=success,
        risk_score=risk_score,
        action_taken=action
    )
    db.add(event)
    db.commit()
    return event