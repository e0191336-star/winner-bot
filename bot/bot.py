import os
import csv
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import FastAPI, Depends, Header, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from loguru import logger

load_dotenv()

API_KEY = os.getenv("API_KEY", "")
CSV_LOG_FILE = os.getenv("CSV_LOG_FILE", "bot/logdata/signals.csv")
ROTATING_LOG_FILE = os.getenv("ROTATING_LOG_FILE", "bot/logdata/app.log")
DEFAULT_PAIRS = [p.strip() for p in os.getenv("DEFAULT_PAIRS", "BTC-USD,ETH-USD").split(",") if p.strip()]
DEFAULT_TIMEFRAMES = [t.strip() for t in os.getenv("DEFAULT_TIMEFRAMES", "1m,5m,15m").split(",") if t.strip()]

os.makedirs(os.path.dirname(CSV_LOG_FILE), exist_ok=True)
logger.add(ROTATING_LOG_FILE, rotation="10 MB")

app = FastAPI(title="Winner Bot API", version="0.1.0")


class Signal(BaseModel):
	pair: str
	timeframe: str
	timestamp: datetime
	action: str
	confidence: float
	reasons: List[str] = []


class UserStatus(BaseModel):
	email: str
	trial_expires_at: Optional[datetime]
	subscription: Optional[str]
	is_blocked: bool


class AdminMetrics(BaseModel):
	active_users: int
	signals_last_24h: int
	accuracy_7d: float


def require_api_key(x_api_key: str = Header("")):
	if API_KEY and x_api_key == API_KEY:
		return True
	raise HTTPException(status_code=401, detail="Invalid API key")


_latest_signals: Dict[str, Signal] = {}
_history: List[Signal] = []


@app.get("/signals/latest", response_model=Dict[str, Signal])
async def get_latest_signals():
	return _latest_signals


@app.get("/signals/history", response_model=List[Signal])
async def get_signal_history(limit: int = 200):
	return _history[-limit:]


@app.get("/user/status", response_model=UserStatus)
async def get_user_status(email: str):
	now = datetime.utcnow()
	trial_expires = now + timedelta(days=7)
	return UserStatus(email=email, trial_expires_at=trial_expires, subscription=None, is_blocked=False)


@app.get("/admin/metrics", response_model=AdminMetrics, dependencies=[Depends(require_api_key)])
async def get_admin_metrics():
	return AdminMetrics(active_users=1, signals_last_24h=len([s for s in _history if s.timestamp > datetime.utcnow() - timedelta(days=1)]), accuracy_7d=0.0)


@app.get("/contact")
async def contact():
	return {"email": os.getenv("ADMIN_EMAIL", ""), "wallet": os.getenv("USER_WALLET_ADDRESS", "")} 


@app.get("/terms")
async def terms():
	return {"markdown": open("docs/terms.md", "r", encoding="utf-8").read() if os.path.exists("docs/terms.md") else ""}


@app.get("/privacy")
async def privacy():
	return {"markdown": open("docs/privacy.md", "r", encoding="utf-8").read() if os.path.exists("docs/privacy.md") else ""}


# Placeholder scheduler: simulate signals

def log_signal(signal: Signal) -> None:
	_history.append(signal)
	_latest_signals[f"{signal.pair}:{signal.timeframe}"] = signal
	file_exists = os.path.exists(CSV_LOG_FILE)
	with open(CSV_LOG_FILE, "a", newline="", encoding="utf-8") as f:
		writer = csv.DictWriter(f, fieldnames=["timestamp", "pair", "timeframe", "action", "confidence", "reasons"])
		if not file_exists:
			writer.writeheader()
		writer.writerow({
			"timestamp": signal.timestamp.isoformat(),
			"pair": signal.pair,
			"timeframe": signal.timeframe,
			"action": signal.action,
			"confidence": f"{signal.confidence:.2f}",
			"reasons": "; ".join(signal.reasons),
		})
	logger.info(f"Logged signal: {signal.pair} {signal.timeframe} {signal.action} conf={signal.confidence:.2f}")


def generate_dummy_signal() -> None:
	for pair in DEFAULT_PAIRS:
		for timeframe in DEFAULT_TIMEFRAMES:
			s = Signal(pair=pair, timeframe=timeframe, timestamp=datetime.utcnow(), action="BUY", confidence=0.82, reasons=["RSI", "EMA"])
			log_signal(s)


if __name__ == "__main__":
	# For local debug: simulate a periodic signal generation
	logger.info("Starting Winner Bot in demo mode...")
	while True:
		generate_dummy_signal()
		time.sleep(15)