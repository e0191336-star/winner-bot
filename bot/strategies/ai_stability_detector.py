from typing import List, Optional, Tuple
import pandas as pd


def ai_stability_signal(df: pd.DataFrame) -> Optional[Tuple[str, float, List[str]]]:
	# Placeholder: low volatility favors trend continuation (use EMA relationship)
	if "ema_short" not in df.columns or "ema_long" not in df.columns:
		return None
	vol = float((df["close"].pct_change().rolling(20).std().iloc[-1] or 0.0))
	if vol != vol:
		return None
	es = float(df["ema_short"].iloc[-1])
	el = float(df["ema_long"].iloc[-1])
	if vol < 0.004:  # low volatility
		action = "BUY" if es >= el else "SELL"
		return (action, 0.7, ["Low volatility trend-continuation"])
	return None