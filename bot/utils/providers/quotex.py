import os
from typing import List, Dict, Any

import pandas as pd

_TIMEFRAME_MAP = {"1m": 60, "5m": 300, "15m": 900}


def _import_any_client():
	"""Attempt to import one of the unofficial Quotex libraries.
	Returns a tuple (name, module) or (None, None) if none are installed.
	"""
	try:
		from quotexapi.stable_api import Quotex as QxClient  # type: ignore
		return ("quotexapi", QxClient)
	except Exception:
		pass
	try:
		# Some forks name it pythonquotex
		from pythonquotex.stable_api import Quotex as QxClient  # type: ignore
		return ("pythonquotex", QxClient)
	except Exception:
		pass
	try:
		# pyquotex variants
		from pyquotex.client import Quotex as QxClient  # type: ignore
		return ("pyquotex", QxClient)
	except Exception:
		pass
	return (None, None)


def fetch_candles(pair: str, timeframe: str, limit: int = 200) -> pd.DataFrame:
	"""Fetch candles for an OTC-style pair using unofficial Quotex client if available.
	- Requires environment variables QUOTEX_EMAIL/QUOTEX_PASSWORD or QUOTEX_SESSION
	- Returns DataFrame with columns: open, high, low, close, volume
	If client or credentials are missing, returns an empty DataFrame.
	"""
	tf = _TIMEFRAME_MAP.get(timeframe, 60)
	name, Client = _import_any_client()
	if not Client:
		return pd.DataFrame()

	email = os.getenv("QUOTEX_EMAIL", "").strip()
	password = os.getenv("QUOTEX_PASSWORD", "").strip()
	session = os.getenv("QUOTEX_SESSION", "").strip()
	if not (session or (email and password)):
		return pd.DataFrame()

	try:
		client = Client(email, password) if email and password else Client(session=session)
		# Common API patterns across forks:
		# - client.connect(); client.get_profile()
		# - client.get_assets(); client.get_candles(asset, interval, count)
		if hasattr(client, "connect"):
			client.connect()
		# Resolve asset/instrument identifier
		asset = None
		if hasattr(client, "get_assets"):
			assets = client.get_assets()  # type: ignore
			# Try to match by name/symbol
			needle = pair.upper().replace(" ", "").replace("-OTC", "").replace("_OTC", "")
			for a in assets:
				label = str(a.get("symbol") or a.get("name") or a).upper().replace(" ", "")
				if needle in label or label in needle:
					asset = a
					break
		# Fallback to using the pair directly if API accepts strings
		asset_arg = asset if asset is not None else pair
		candles: List[Dict[str, Any]] = []
		if hasattr(client, "get_candles"):
			candles = client.get_candles(asset_arg, tf, limit)  # type: ignore
		elif hasattr(client, "candles"):
			candles = client.candles(asset_arg, tf, limit)  # type: ignore
		else:
			return pd.DataFrame()
		# Normalize
		if not candles:
			return pd.DataFrame()
		rows = []
		for c in candles:
			# Try common key names across forks
			open_ = float(c.get("open") or c.get("o") or c.get("Open") or c.get("O") or c.get("open_price") or c.get("start_price") or 0)
			high = float(c.get("high") or c.get("h") or c.get("High") or c.get("H") or open_)
			low = float(c.get("low") or c.get("l") or c.get("Low") or c.get("L") or open_)
			close = float(c.get("close") or c.get("c") or c.get("Close") or c.get("C") or c.get("close_price") or c.get("end_price") or open_)
			vol = float(c.get("volume") or c.get("v") or 0)
			rows.append((open_, high, low, close, vol))
		df = pd.DataFrame(rows, columns=["open", "high", "low", "close", "volume"])
		return df
	except Exception:
		return pd.DataFrame()
	finally:
		try:
			if hasattr(client, "close"):
				client.close()
		except Exception:
			pass