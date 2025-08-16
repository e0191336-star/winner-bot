from typing import Tuple

_CCY = {"USD","EUR","GBP","JPY","AUD","NZD","CAD","CHF","CNY","HKD","INR","RUB","TRY"}


def is_otc_pair(pair: str) -> bool:
	p = pair.upper().replace(" ", "")
	return p.endswith("-OTC") or p.endswith("_OTC")


def strip_otc_suffix(pair: str) -> str:
	p = pair.replace(" ", "")
	for suf in ("-OTC", "_OTC"):
		if p.upper().endswith(suf):
			return p[: -len(suf)]
	return p


def to_yfinance_symbol(underlying: str) -> str:
	# Crypto e.g. BTC-USD -> BTC-USD
	if "-" in underlying:
		base, quote = underlying.split("-", 1)
		if base.upper() not in _CCY and quote.upper() not in _CCY:
			return f"{base.upper()}-{quote.upper()}"
		# FX e.g. EUR-USD -> EURUSD=X
		if base.upper() in _CCY and quote.upper() in _CCY:
			return f"{base.upper()}{quote.upper()}=X"
		return underlying
	# 6-letter FX: EURUSD -> EURUSD=X
	if len(underlying) == 6 and underlying[:3].upper() in _CCY and underlying[3:].upper() in _CCY:
		return f"{underlying.upper()}=X"
	return underlying