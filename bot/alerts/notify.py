import time
from typing import Dict, Tuple

_last_sent: Dict[Tuple[str, str, str], float] = {}


def should_notify(pair: str, timeframe: str, action: str, cooldown_seconds: int = 60) -> bool:
	key = (pair, timeframe, action)
	now = time.time()
	last = _last_sent.get(key, 0.0)
	if now - last >= cooldown_seconds:
		_last_sent[key] = now
		return True
	return False


def notify_admin(subject: str, body: str) -> None:
	# Placeholder; integrate email/Firebase here
	print(f"[ADMIN ALERT] {subject}: {body}")