from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from database import Base
from datetime import datetime

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
    explanation = Column(Text, default="")

class OTPRecord(Base):
    __tablename__ = "otp_records"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String)
    otp_code = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime)
    is_used = Column(Boolean, default=False)