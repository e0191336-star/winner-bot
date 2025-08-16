from typing import List, Optional, Tuple
import pandas as pd


def bollinger_signal(df: pd.DataFrame) -> Optional[Tuple[str, float, List[str]]]:
	for col in ("bb_low", "bb_mid", "bb_high"):
		if col not in df.columns or df[col].isna().all():
			return None
	c = float(df["close"].iloc[-1])
	low = float(df["bb_low"].iloc[-1])
	high = float(df["bb_high"].iloc[-1])
	if c <= low:
		return ("BUY", 0.7, ["Touch lower band"])
	if c >= high:
		return ("SELL", 0.7, ["Touch upper band"])
	return None