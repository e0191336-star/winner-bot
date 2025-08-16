import os
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import pandas_ta as ta
from .providers.binance import fetch_klines
from .providers.yahoo import fetch_candles as yahoo_fetch
from .providers.quotex import fetch_candles as quotex_fetch
from .otc import is_otc_pair, strip_otc_suffix, to_yfinance_symbol


def map_pair_to_ticker(pair: str) -> str:
	# Simple mapping; extend as needed for specific broker symbols
	return pair.replace("/", "-")


def timeframe_to_interval(timeframe: str) -> str:
	lookup = {"1m": "1m", "5m": "5m", "15m": "15m"}
	return lookup.get(timeframe, "1m")


def get_candles(pair: str, timeframe: str, limit: int = 200) -> pd.DataFrame:
	"""Fetch OHLCV data for a pair and timeframe.
	- OTC: try Quotex (if enabled and creds present) then Yahoo fallback
	- Non-OTC: Binance public REST
	"""
	use_quotex = os.getenv("QUOTEX_ENABLED", "false").lower() == "true"
	if is_otc_pair(pair):
		underlying = strip_otc_suffix(pair)
		if use_quotex:
			df = quotex_fetch(underlying, timeframe, limit)
			if df is None or df.empty:
				# fallback
				symbol = to_yfinance_symbol(map_pair_to_ticker(underlying))
				df = yahoo_fetch(symbol, timeframe, limit)
		else:
			symbol = to_yfinance_symbol(map_pair_to_ticker(underlying))
			df = yahoo_fetch(symbol, timeframe, limit)
	else:
		df = fetch_klines(pair, timeframe, limit)
	if not isinstance(df, pd.DataFrame) or df.empty:
		return pd.DataFrame()
	# Indicators
	df["rsi"] = ta.rsi(df["close"], length=14)
	macd = ta.macd(df["close"], fast=12, slow=26, signal=9)
	if macd is not None and not macd.empty:
		df["macd"] = macd[macd.columns[0]]
		df["macd_signal"] = macd[macd.columns[1]]
		df["macd_hist"] = macd[macd.columns[2]]
	ema_short = ta.ema(df["close"], length=9)
	ema_long = ta.ema(df["close"], length=21)
	df["ema_short"] = ema_short
	df["ema_long"] = ema_long
	bb = ta.bbands(df["close"], length=20, std=2)
	if bb is not None and not bb.empty:
		df["bb_low"] = bb[bb.columns[0]]
		df["bb_mid"] = bb[bb.columns[1]]
		df["bb_high"] = bb[bb.columns[2]]
	# Volume moving average for spike detection
	df["vol_ma"] = df["volume"].rolling(20).mean()
	return df.tail(limit).copy()