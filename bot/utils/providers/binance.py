import time
from typing import List

import pandas as pd
import requests

_INTERVAL_MAP = {
	"1m": "1m",
	"5m": "5m",
	"15m": "15m",
}


def to_binance_symbol(pair: str) -> str:
	# Convert BTC-USD -> BTCUSDT by default
	base, quote = pair.replace("/", "-").split("-")
	if quote.upper() in ("USD", "USDT"):
		quote = "USDT"
	return f"{base.upper()}{quote.upper()}"


def fetch_klines(pair: str, timeframe: str, limit: int = 200) -> pd.DataFrame:
	symbol = to_binance_symbol(pair)
	interval = _INTERVAL_MAP.get(timeframe, "1m")
	url = "https://api.binance.com/api/v3/klines"
	params = {"symbol": symbol, "interval": interval, "limit": min(limit, 1000)}
	r = requests.get(url, params=params, timeout=10)
	r.raise_for_status()
	data: List[List] = r.json()
	if not data:
		return pd.DataFrame()
	# columns: open time, open, high, low, close, volume, close time, ...
	df = pd.DataFrame(data, columns=[
		"open_time","open","high","low","close","volume","close_time",
		"qav","num_trades","taker_base","taker_quote","ignore"
	])
	df = df[["open","high","low","close","volume"]].astype(float)
	return df