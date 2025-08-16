import os
import json
from contextlib import contextmanager
from typing import List, Dict, Any, Optional

import pandas as pd

try:
	from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
	has_playwright = True
except Exception:
	has_playwright = False


def _env(name: str, default: str = "") -> str:
	return os.getenv(name, default)


@contextmanager
def _browser():
	if not has_playwright:
		raise RuntimeError("Playwright not installed")
	with sync_playwright() as p:
		browser = p.chromium.launch(headless=True)
		context = browser.new_context()
		page = context.new_page()
		try:
			yield page
		finally:
			context.close()
			browser.close()


def _login(page) -> None:
	base = _env("QUOTEX_BASE_URL", "https://quotex.io").rstrip("/")
	email = _env("QUOTEX_EMAIL", "")
	password = _env("QUOTEX_PASSWORD", "")
	if not email or not password:
		raise RuntimeError("Missing QUOTEX_EMAIL or QUOTEX_PASSWORD")
	page.goto(f"{base}/en/sign-in", timeout=60000)
	# Try common selectors; adjust as needed
	selectors = {
		"email": _env("QUOTEX_SEL_EMAIL", 'input[type="email"]'),
		"password": _env("QUOTEX_SEL_PASSWORD", 'input[type="password"]'),
		"submit": _env("QUOTEX_SEL_SUBMIT", 'button[type="submit"]'),
	}
	page.wait_for_selector(selectors["email"], timeout=30000)
	page.fill(selectors["email"], email)
	page.fill(selectors["password"], password)
	page.click(selectors["submit"]) 
	# Wait for trade room or profile
	page.wait_for_load_state("networkidle", timeout=60000)


def fetch_candles(pair: str, timeframe: str, limit: int = 200) -> pd.DataFrame:
	"""Attempt to fetch candles by intercepting Quotex trade room network calls.
	This is best-effort and depends on the current site implementation.
	Environment variables:
	- QUOTEX_BASE_URL
	- QUOTEX_EMAIL / QUOTEX_PASSWORD
	- QUOTEX_TRADE_PATH (default '/trade')
	"""
	if not has_playwright:
		return pd.DataFrame()
	trade_path = _env("QUOTEX_TRADE_PATH", "/trade")
	try:
		with _browser() as page:
			_login(page)
			base = _env("QUOTEX_BASE_URL", "https://quotex.io").rstrip("/")
			# Navigate to trade room
			page.goto(f"{base}{trade_path}", timeout=60000)

			captured: List[Dict[str, Any]] = []
			def on_response(resp):
				try:
					url = resp.url
					if any(k in url for k in ["candles", "ohlc", "chart", "history"]):
						data = resp.json()
						# Heuristic: find list of candles
						if isinstance(data, dict):
							for key, val in data.items():
								if isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict):
									captured.extend(val)
						elif isinstance(data, list):
							captured.extend(data)
				except Exception:
					pass
			page.on("response", on_response)
			# Interact to switch pair/timeframe if selectors are known (skipped: site-specific)
			page.wait_for_timeout(4000)
			page.wait_for_load_state("networkidle", timeout=60000)
			# Build DataFrame
			rows: List[List[float]] = []
			for c in captured[-limit:]:
				open_ = float(c.get("open") or c.get("o") or c.get("Open") or 0)
				high = float(c.get("high") or c.get("h") or c.get("High") or open_)
				low = float(c.get("low") or c.get("l") or c.get("Low") or open_)
				close = float(c.get("close") or c.get("c") or c.get("Close") or open_)
				vol = float(c.get("volume") or c.get("v") or 0)
				rows.append([open_, high, low, close, vol])
			df = pd.DataFrame(rows, columns=["open", "high", "low", "close", "volume"])
			return df.tail(limit)
	except Exception:
		return pd.DataFrame()