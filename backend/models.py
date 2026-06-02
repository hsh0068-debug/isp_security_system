from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    email = Column(String)
    created_at = Column(DateTime, default=func.now())

class LoginEvent(Base):
    __tablename__ = "login_events"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    ip_address = Column(String)
    location = Column(String)
    device_type = Column(String)
    login_time = Column(DateTime, default=func.now())
    success = Column(Boolean, default=True)
    risk_score = Column(Float, default=0.0)
    action_taken = Column(String, default="allow")