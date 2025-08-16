from typing import List, Optional, Tuple
import pandas as pd


def rsi_signal(df: pd.DataFrame) -> Optional[Tuple[str, float, List[str]]]:
	if "rsi" not in df.columns or df["rsi"].isna().all():
		return None
	rsi = float(df["rsi"].iloc[-1])
	if rsi <= 30:
		return ("BUY", min(0.9, (30 - rsi) / 30.0 + 0.6), ["RSI<=30 Oversold"])
	if rsi >= 70:
		return ("SELL", min(0.9, (rsi - 70) / 30.0 + 0.6), ["RSI>=70 Overbought"])
	return None