from typing import List, Optional, Tuple
import pandas as pd


def pattern_signal(df: pd.DataFrame) -> Optional[Tuple[str, float, List[str]]]:
	if len(df) < 2:
		return None
	prev_open = float(df["open"].iloc[-2])
	prev_close = float(df["close"].iloc[-2])
	open_ = float(df["open"].iloc[-1])
	close = float(df["close"].iloc[-1])
	# Bullish engulfing
	if prev_close < prev_open and close > open_ and close >= prev_open and open_ <= prev_close:
		return ("BUY", 0.66, ["Bullish engulfing"])
	# Bearish engulfing
	if prev_close > prev_open and close < open_ and close <= prev_open and open_ >= prev_close:
		return ("SELL", 0.66, ["Bearish engulfing"])
	return None