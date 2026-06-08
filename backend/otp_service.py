import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import OTPRecord
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


def create_otp(db: Session, username: str, email: str):
    db.query(OTPRecord).filter(
        OTPRecord.username == username
    ).delete()
    db.commit()

    otp_code = generate_otp()
    expires_at = datetime.now() + timedelta(minutes=5)

    otp_record = OTPRecord(
        username=username,
        email=email,
        otp_code=otp_code,
        expires_at=expires_at,
        is_used=False
    )
    db.add(otp_record)
    db.commit()

    return otp_code


def verify_otp(db: Session, username: str, otp_code: str):
    record = db.query(OTPRecord).filter(
        OTPRecord.username == username,
        OTPRecord.otp_code == otp_code,
        OTPRecord.is_used == False
    ).first()

    if not record:
        return False, "Invalid OTP code"

    if datetime.now() > record.expires_at:
        return False, "OTP has expired"

    record.is_used = True
    db.commit()

    return True, "OTP verified successfully"


def send_otp_email(email: str, username: str, otp_code: str):
    try:
        SENDER_EMAIL = "madhavihennayaka@gmail.com"
        SENDER_PASSWORD = "tsyh zbuw plnn sswh"

        msg = MIMEMultipart('alternative')
        msg['Subject'] = "ISP Security System - Your OTP Code"
        msg['From'] = SENDER_EMAIL
        msg['To'] = email

        html_body = f"""
        <html>
        <body style="font-family:Arial,sans-serif;">
            <div style="background:#0D1B3E;padding:20px;border-radius:10px;">
                <h2 style="color:#02C39A;">ISP Security System</h2>
                <p style="color:white;">Hello {username},</p>
                <p style="color:#aaa;">Your One-Time Password:</p>
                <h1 style="color:#02C39A;font-size:40px;letter-spacing:10px;">{otp_code}</h1>
                <p style="color:#aaa;font-size:12px;">Expires in 5 minutes</p>
            </div>
        </body>
        </html>
        """

        part = MIMEText(html_body, 'html')
        msg.attach(part)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, email, msg.as_string())

        return True, "OTP sent successfully"

    except Exception as e:
        print(f"Email error: {e}")
        print(f"TEST MODE - OTP for {username}: {otp_code}")
        return False, f"Test mode - OTP is: {otp_code}"