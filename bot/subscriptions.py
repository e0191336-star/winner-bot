from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from .db import get_store

store = get_store()

TRIAL_DAYS = 7


def get_status(email: str) -> Dict[str, Any]:
	user = store.get_user(email) or {}
	trial_start = user.get("trial_start") or user.get("created_at") or datetime.utcnow()
	trial_expires = trial_start + timedelta(days=TRIAL_DAYS)
	subscription = user.get("subscription")  # e.g., {"plan": "monthly", "expires_at": dt}
	is_blocked = False
	if subscription:
		exp = subscription.get("expires_at")
		if isinstance(exp, str):
			try:
				exp = datetime.fromisoformat(exp)
			except Exception:
				exp = None
		if exp and datetime.utcnow() > exp:
			is_blocked = True
	elif datetime.utcnow() > trial_expires:
		is_blocked = True
	return {
		"trial_expires_at": trial_expires,
		"subscription": subscription,
		"is_blocked": is_blocked,
	}