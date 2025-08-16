from typing import Optional

import pandas as pd
import yfinance as yf


def fetch_candles(symbol: str, timeframe: str, limit: int = 200) -> pd.DataFrame:
	interval = {"1m": "1m", "5m": "5m", "15m": "15m"}.get(timeframe, "1m")
	period = "7d" if interval == "1m" else "60d"
	df = yf.download(tickers=symbol, interval=interval, period=period, progress=False)
	if not isinstance(df, pd.DataFrame) or df.empty:
		return pd.DataFrame()
	df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
	return df[["open", "high", "low", "close", "volume"]].copy()