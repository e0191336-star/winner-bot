from typing import Tuple

_CCY = {"USD","EUR","GBP","JPY","AUD","NZD","CAD","CHF","CNY","HKD","INR","RUB","TRY","XAU","XAG"}


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
	# If already dashed: map FX to =X; otherwise keep BASE-QUOTE form
	if "-" in underlying:
		base, quote = underlying.split("-", 1)
		if base.upper() in _CCY and quote.upper() in _CCY:
			return f"{base.upper()}{quote.upper()}=X"
		return f"{base.upper()}-{quote.upper()}"
	# Handle undashed inputs
	up = underlying.upper()
	# 6-letter FX like EURUSD -> EURUSD=X
	if len(up) == 6 and up[:3] in _CCY and up[3:] in _CCY:
		return f"{up}=X"
	# Generic BASEQUOTE where QUOTE is fiat/metal (e.g., BTCUSD) -> BASE-USD
	if len(up) > 3 and up[-3:] in _CCY and up[:-3] not in _CCY:
		return f"{up[:-3]}-{up[-3:]}"
	return underlying