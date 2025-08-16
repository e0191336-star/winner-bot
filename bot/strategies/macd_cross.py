from typing import List, Optional, Tuple
import pandas as pd


def macd_signal(df: pd.DataFrame) -> Optional[Tuple[str, float, List[str]]]:
	for col in ("macd", "macd_signal"):
		if col not in df.columns or df[col].isna().all():
			return None
	macd = float(df["macd"].iloc[-1])
	signal = float(df["macd_signal"].iloc[-1])
	prev_macd = float(df["macd"].iloc[-2])
	prev_signal = float(df["macd_signal"].iloc[-2])
	if prev_macd < prev_signal and macd > signal:
		return ("BUY", 0.75, ["MACD bull cross"])
	if prev_macd > prev_signal and macd < signal:
		return ("SELL", 0.75, ["MACD bear cross"])
	return None