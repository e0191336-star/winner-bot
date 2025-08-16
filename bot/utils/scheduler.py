import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List, Optional, Tuple

import pandas as pd

from ..alerts.notify import should_notify
from ..strategies import enabled as enabled_strategies
from ..strategies.rsi_extreme import rsi_signal
from ..strategies.macd_cross import macd_signal
from ..strategies.ema_crossover import ema_signal
from ..strategies.bollinger_band import bollinger_signal
from ..strategies.volume_spike import volume_spike_signal
from ..strategies.pattern_recognition import pattern_signal
from ..strategies.ai_stability_detector import ai_stability_signal
from .data import get_candles


StrategyFn = Callable[[pd.DataFrame], Optional[Tuple[str, float, List[str]]]]

STRATEGY_MAP: Dict[str, StrategyFn] = {
	"rsi_extreme": rsi_signal,
	"macd_cross": macd_signal,
	"ema_crossover": ema_signal,
	"bollinger_band": bollinger_signal,
	"volume_spike": volume_spike_signal,
	"pattern_recognition": pattern_signal,
	"ai_stability_detector": ai_stability_signal,
}


@dataclass
class EvaluatedSignal:
	pair: str
	timeframe: str
	action: str
	confidence: float
	reasons: List[str]


class SignalEngine:
	def __init__(self, pairs: List[str], timeframes: List[str], min_confirmations: int = 2):
		self.pairs = pairs
		self.timeframes = timeframes
		self.min_confirmations = min_confirmations
		self._stop = False

	def stop(self):
		self._stop = True

	def run_forever(self, on_signal: Callable[[EvaluatedSignal], None], interval_seconds: int = 15):
		while not self._stop:
			for pair in self.pairs:
				for timeframe in self.timeframes:
					self._evaluate_pair_timeframe(pair, timeframe, on_signal)
			time.sleep(interval_seconds)

	def _evaluate_pair_timeframe(self, pair: str, timeframe: str, on_signal: Callable[[EvaluatedSignal], None]):
		df = get_candles(pair, timeframe, limit=200)
		if df is None or df.empty:
			return
		confirmations: List[Tuple[str, float, List[str]]] = []
		for name, cfg in enabled_strategies.ENABLED_STRATEGIES.items():
			fn = STRATEGY_MAP.get(name)
			if not fn:
				continue
			res = fn(df)
			if res is None:
				continue
			confirmations.append(res)

		if len(confirmations) < self.min_confirmations:
			return
		# Determine consensus side and confidence
		actions = [a for (a, _, _) in confirmations]
		buy_votes = actions.count("BUY")
		sell_votes = actions.count("SELL")
		action = "BUY" if buy_votes >= sell_votes else "SELL"
		confidences = [c for (a, c, _) in confirmations if a == action]
		avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
		reasons: List[str] = []
		for a, c, rs in confirmations:
			if a == action:
				reasons.extend(rs)

		evaluated = EvaluatedSignal(pair=pair, timeframe=timeframe, action=action, confidence=avg_conf, reasons=sorted(set(reasons))[:4])
		if should_notify(pair, timeframe, action):
			on_signal(evaluated)


class EngineThread:
	def __init__(self, engine: SignalEngine, on_signal: Callable[[EvaluatedSignal], None], interval_seconds: int = 15):
		self.engine = engine
		self.on_signal = on_signal
		self.interval_seconds = interval_seconds
		self._thread: Optional[threading.Thread] = None

	def start(self):
		if self._thread and self._thread.is_alive():
			return
		self._thread = threading.Thread(target=self.engine.run_forever, args=(self.on_signal, self.interval_seconds), daemon=True)
		self._thread.start()

	def stop(self):
		self.engine.stop()
		if self._thread:
			self._thread.join(timeout=5)