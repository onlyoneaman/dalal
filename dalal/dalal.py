"""Dalal — single entry point for Indian stock exchange data.

All methods return raw API responses. No enforced schema — if the
exchange adds new fields, they flow through automatically.
"""

from __future__ import annotations

from datetime import date

from dalal.errors import ValidationError


class Dalal:
    """Unified API for Indian stock exchanges (NSE + BSE).

    Methods default to NSE. Pass exchange="BSE" for BSE-specific calls.
    BSE-only methods (fundamentals, meta, result_calendar) don't need
    the exchange parameter.
    """

    def __init__(self, *, nse_rate: int | None = None, bse_rate: int | None = None):
        self._nse = None
        self._bse = None
        self._nse_rate = nse_rate
        self._bse_rate = bse_rate

    def _get_nse(self):
        if self._nse is None:
            from dalal.nse import NSESession

            nse = NSESession()
            if self._nse_rate:
                nse.RATE_LIMIT = self._nse_rate
                nse._min_interval = 1.0 / self._nse_rate
            self._nse = nse
        return self._nse

    def _get_bse(self):
        if self._bse is None:
            from dalal.bse import BSESession

            bse = BSESession()
            if self._bse_rate:
                bse.RATE_LIMIT = self._bse_rate
                bse._min_interval = 1.0 / self._bse_rate
            self._bse = bse
        return self._bse

    def _validate_exchange(self, exchange: str) -> str:
        exchange = exchange.upper()
        if exchange not in ("NSE", "BSE"):
            raise ValidationError(
                f"Invalid exchange: {exchange!r}. Use 'NSE' or 'BSE'."
            )
        return exchange

    # --- Context manager ---

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self) -> None:
        if self._nse:
            self._nse.close()
        if self._bse:
            self._bse.close()

    # --- Dual-exchange methods ---

    def quote(self, symbol: str, *, exchange: str = "NSE"):
        exchange = self._validate_exchange(exchange)
        if exchange == "NSE":
            return self._get_nse().quote(symbol)
        return self._get_bse().quote(symbol)

    def history(
        self,
        symbol: str,
        start: str | date,
        end: str | date,
        *,
        exchange: str = "NSE",
        series: str = "EQ",
    ):
        exchange = self._validate_exchange(exchange)
        if exchange == "NSE":
            return self._get_nse().history(symbol, start, end, series=series)
        raise ValidationError("BSE history not yet supported. Use exchange='NSE'.")

    def actions(self, symbol: str | None = None, *, exchange: str = "NSE"):
        exchange = self._validate_exchange(exchange)
        if exchange == "NSE":
            return self._get_nse().actions(symbol)
        return self._get_bse().actions(symbol)

    def gainers(self, index: str | None = None, *, exchange: str = "NSE"):
        exchange = self._validate_exchange(exchange)
        if exchange == "NSE":
            return self._get_nse().gainers(index or "NIFTY 50")
        return self._get_bse().gainers()

    def losers(self, index: str | None = None, *, exchange: str = "NSE"):
        exchange = self._validate_exchange(exchange)
        if exchange == "NSE":
            return self._get_nse().losers(index or "NIFTY 50")
        return self._get_bse().losers()

    def announcements(self, symbol: str | None = None, *, exchange: str = "NSE"):
        exchange = self._validate_exchange(exchange)
        if exchange == "NSE":
            return self._get_nse().announcements(symbol)
        return self._get_bse().announcements(symbol)

    def status(self, *, exchange: str = "NSE"):
        exchange = self._validate_exchange(exchange)
        if exchange == "NSE":
            return self._get_nse().status()
        return self._get_bse().status()

    def lookup(self, query: str, *, exchange: str = "NSE"):
        exchange = self._validate_exchange(exchange)
        if exchange == "NSE":
            return self._get_nse().lookup(query)
        return self._get_bse().lookup(query)

    # --- NSE-only methods ---

    def bulk_deals(
        self, start: str | date, end: str | date, option_type: str = "bulk_deals"
    ):
        return self._get_nse().bulk_deals(start, end, option_type=option_type)

    def block_deals(self):
        return self._get_nse().block_deals()

    def holidays(self, holiday_type: str = "trading"):
        return self._get_nse().holidays(holiday_type)

    def index(self, name: str = "NIFTY 50"):
        return self._get_nse().index(name)

    def shareholding(self, symbol: str):
        return self._get_nse().shareholding(symbol)

    def advances(self):
        return self._get_nse().advances()

    # --- BSE-only methods ---

    def fundamentals(self, scripcode: str):
        return self._get_bse().fundamentals(scripcode)

    def meta(self, scripcode: str):
        return self._get_bse().meta(scripcode)

    def result_calendar(self, scripcode: str | None = None):
        return self._get_bse().result_calendar(scripcode)
