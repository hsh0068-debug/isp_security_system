from fastapi import FastAPI, Depends, Request
from sqlalchemy.orm import Session
from database import engine, get_db, SessionLocal
import models
import auth

app = FastAPI(title="ISP Security System")

# Creates all tables in database automatically
models.Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "ISP Security System is running!"}

@app.post("/register")
def register(username: str, password: str, email: str, 
             db: Session = Depends(get_db)):
    # Check if user already exists
    existing = auth.get_user(db, username)
    if existing:
        return {"error": "Username already exists"}
    
    # Create new user
    user = auth.create_user(db, username, password, email)
    return {"message": f"User {username} created successfully!"}

@app.post("/login")
def login(username: str, password: str, request: Request,
          db: Session = Depends(get_db)):
    # Check if user exists
    user = auth.get_user(db, username)
    if not user:
        return {"error": "User not found"}
    
    # Check password
    if not auth.verify_password(password, user.password_hash):
        # Save failed login event
        auth.save_login_event(
            db, username, 
            ip=request.client.host,
            location="Unknown",
            device="Unknown",
            success=False,
            risk_score=50.0,
            action="blocked"
        )
        return {"error": "Wrong password"}
    
    # Save successful login event
    auth.save_login_event(
        db, username,
        ip=request.client.host,
        location="Colombo",
        device="Browser",
        success=True,
        risk_score=10.0,
        action="allow"
    )
    return {"message": f"Welcome {username}! Login successful!"}

@app.get("/login-events")
def get_login_events(db: Session = Depends(get_db)):
    events = db.query(models.LoginEvent).all()
    return events