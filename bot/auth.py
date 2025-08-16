import os
import random
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from .db import get_store

JWT_SECRET = os.getenv("JWT_SECRET", "change-this-secret")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD", "")
SMTP_SENDER = os.getenv("SMTP_SENDER", "") or SMTP_USERNAME

router = APIRouter(prefix="/auth", tags=["auth"])
store = get_store()


class SendOtpRequest(BaseModel):
	email: EmailStr


class VerifyOtpRequest(BaseModel):
	email: EmailStr
	code: str


def _send_email(to_email: str, code: str):
	msg = MIMEText(f"Your Winner Bot OTP code is: {code}. It expires in 5 minutes.")
	msg["Subject"] = "Your OTP Code"
	msg["From"] = SMTP_SENDER
	msg["To"] = to_email
	with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
		server.starttls()
		if SMTP_USERNAME and SMTP_PASSWORD:
			server.login(SMTP_USERNAME, SMTP_PASSWORD)
		server.sendmail(SMTP_SENDER, [to_email], msg.as_string())


@router.post("/send-otp")
async def send_otp(req: SendOtpRequest):
	code = f"{random.randint(100000, 999999)}"
	expires_at = datetime.utcnow() + timedelta(minutes=5)
	store.save_otp(req.email, code, expires_at)
	try:
		_send_email(req.email, code)
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to send OTP: {e}")
	return {"ok": True}


@router.post("/verify-otp")
async def verify_otp(req: VerifyOtpRequest):
	if not store.consume_otp(req.email, req.code):
		raise HTTPException(status_code=400, detail="Invalid or expired code")
	# Create or update user trial/subscription placeholder
	user = store.upsert_user(req.email, {"last_login": datetime.utcnow()})
	payload = {"sub": req.email, "exp": datetime.utcnow() + timedelta(days=7)}
	token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
	return {"token": token, "trial_expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()}