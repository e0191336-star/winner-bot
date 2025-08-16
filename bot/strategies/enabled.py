from typing import Dict, Any

# Map strategy name to configuration
ENABLED_STRATEGIES: Dict[str, Dict[str, Any]] = {
	"rsi_extreme": {"period": 14, "oversold": 30, "overbought": 70},
	"macd_cross": {"fast": 12, "slow": 26, "signal": 9},
	"ema_crossover": {"short": 9, "long": 21},
	"bollinger_band": {"period": 20, "stddev": 2.0},
	"volume_spike": {"window": 20, "multiplier": 2.5},
	"pattern_recognition": {},
	"ai_stability_detector": {"model": "baseline"},
}