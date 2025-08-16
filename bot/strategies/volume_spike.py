from typing import List, Optional, Tuple
import pandas as pd


def volume_spike_signal(df: pd.DataFrame) -> Optional[Tuple[str, float, List[str]]]:
	if "volume" not in df.columns or "vol_ma" not in df.columns:
		return None
	v = float(df["volume"].iloc[-1])
	vma = float(df["vol_ma"].iloc[-1])
	if vma <= 0:
		return None
	if v >= 2.5 * vma:
		# Direction inferred from candle
		close = float(df["close"].iloc[-1])
		open_ = float(df["open"].iloc[-1])
		action = "BUY" if close > open_ else "SELL"
		return (action, 0.68, ["Volume spike 2.5x"])
	return None