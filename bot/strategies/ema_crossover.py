from typing import List, Optional, Tuple
import pandas as pd


def ema_signal(df: pd.DataFrame) -> Optional[Tuple[str, float, List[str]]]:
	for col in ("ema_short", "ema_long"):
		if col not in df.columns or df[col].isna().all():
			return None
	es = float(df["ema_short"].iloc[-1])
	el = float(df["ema_long"].iloc[-1])
	prev_es = float(df["ema_short"].iloc[-2])
	prev_el = float(df["ema_long"].iloc[-2])
	if prev_es < prev_el and es > el:
		return ("BUY", 0.72, ["EMA bull cross 9/21"])
	if prev_es > prev_el and es < el:
		return ("SELL", 0.72, ["EMA bear cross 9/21"])
	return None