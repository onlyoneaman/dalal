"""NSE exchange session — cookie-primed session, all NSE endpoint implementations."""

from __future__ import annotations

from datetime import date

from dalal.base import Exchange
from dalal.constants import (
    NSE_API,
    NSE_BASE,
    NSE_COOKIE_URL,
    NSE_HEADERS,
    NSE_RATE_LIMIT,
    NSE_TIMEOUT,
)
from dalal.errors import AuthError, DataNotAvailable, SymbolNotFound
from dalal.utils import chunk_dates, clean_date, clean_number, fmt_date_dmy, parse_date


class NSESession(Exchange):
    BASE_URL = NSE_API
    RATE_LIMIT = NSE_RATE_LIMIT
    TIMEOUT = NSE_TIMEOUT

    def __init__(self):
        self._cookies_primed = False
        super().__init__()

    def _init_session(self) -> None:
        self._session.headers.update(NSE_HEADERS)

    def _prime_cookies(self) -> None:
        """Hit NSE option-chain page to acquire session cookies."""
        if self._cookies_primed:
            return
        try:
            self._session.get(NSE_COOKIE_URL, timeout=self.TIMEOUT)
        except Exception:
            pass  # best-effort — cookies may already be valid
        self._cookies_primed = True

    def fetch(self, path: str, params: dict | None = None) -> dict | list:
        """Override to add cookie priming and 401 retry."""
        self._prime_cookies()
        try:
            return super().fetch(path, params)
        except AuthError:
            # Cookie expired — re-prime and retry once
            self._cookies_primed = False
            self._prime_cookies()
            return super().fetch(path, params)

    # --- quote ---

    def quote(self, symbol: str) -> dict:
        data = self.fetch("/quote-equity", params={"symbol": symbol.upper()})
        if not data or "error" in data:
            raise SymbolNotFound(f"NSE symbol not found: {symbol}")
        info = data.get("priceInfo", {})
        meta = data.get("info", {})
        return {
            "symbol": meta.get("symbol", symbol.upper()),
            "name": meta.get("companyName", ""),
            "isin": meta.get("isin", ""),
            "ltp": clean_number(info.get("lastPrice")),
            "open": clean_number(info.get("open")),
            "high": clean_number(info.get("intraDayHighLow", {}).get("max")),
            "low": clean_number(info.get("intraDayHighLow", {}).get("min")),
            "prev_close": clean_number(info.get("previousClose")),
            "change": clean_number(info.get("change")),
            "pct_change": clean_number(info.get("pChange")),
            "year_high": clean_number(info.get("weekHighLow", {}).get("max")),
            "year_low": clean_number(info.get("weekHighLow", {}).get("min")),
        }

    # --- history ---

    def history(
        self,
        symbol: str,
        start: str | date,
        end: str | date,
        series: str = "EQ",
    ) -> list[dict]:
        start_d = parse_date(start)
        end_d = parse_date(end)
        chunks = chunk_dates(start_d, end_d, chunk_days=100)
        all_rows: list[dict] = []
        for c_start, c_end in chunks:
            params = {
                "symbol": symbol.upper(),
                "from": fmt_date_dmy(c_start),
                "to": fmt_date_dmy(c_end),
                "series": f'["{series}"]',
            }
            data = self.fetch("/historical/cm/equity", params=params)
            for r in data.get("data", []):
                all_rows.append(
                    {
                        "date": clean_date(r.get("CH_TIMESTAMP")),
                        "open": clean_number(r.get("CH_OPENING_PRICE")),
                        "high": clean_number(r.get("CH_TRADE_HIGH_PRICE")),
                        "low": clean_number(r.get("CH_TRADE_LOW_PRICE")),
                        "close": clean_number(r.get("CH_CLOSING_PRICE")),
                        "volume": clean_number(r.get("CH_TOT_TRADED_QTY")),
                        "vwap": clean_number(r.get("VWAP")),
                        "delivery_pct": clean_number(r.get("COP_DELIV_PERC")),
                    }
                )
        return all_rows

    # --- actions ---

    def actions(self, symbol: str | None = None) -> list[dict]:
        params: dict = {"index": "equities"}
        if symbol:
            params["symbol"] = symbol.upper()
        data = self.fetch("/corporates-corporateActions", params=params)
        rows = data if isinstance(data, list) else []
        return [
            {
                "symbol": r.get("symbol", "").strip(),
                "name": r.get("comp", "").strip(),
                "isin": r.get("isin", "").strip(),
                "subject": r.get("subject", "").strip(),
                "ex_date": clean_date(r.get("exDate")),
                "record_date": clean_date(r.get("recDate")),
                "series": r.get("series", "").strip(),
            }
            for r in rows
        ]

    # --- bulk_deals ---

    def bulk_deals(self, start: str | date, end: str | date) -> list[dict]:
        params = {
            "from": fmt_date_dmy(parse_date(start)),
            "to": fmt_date_dmy(parse_date(end)),
        }
        data = self.fetch("/historical/bulk-deals", params=params)
        rows = (
            data.get("data", [])
            if isinstance(data, dict)
            else data
            if isinstance(data, list)
            else []
        )
        return [
            {
                "symbol": r.get("symbol", "").strip(),
                "date": clean_date(r.get("date")),
                "client": r.get("clientName", "").strip(),
                "buy_sell": r.get("buySell", "").strip(),
                "quantity": clean_number(r.get("quantityTraded")),
                "price": clean_number(r.get("tradePrice")),
            }
            for r in rows
        ]

    # --- block_deals ---

    def block_deals(self) -> list[dict]:
        data = self.fetch("/block-deal")
        rows = data.get("data", []) if isinstance(data, dict) else []
        return [
            {
                "symbol": r.get("symbol", "").strip(),
                "date": clean_date(r.get("date")),
                "client": r.get("clientName", "").strip(),
                "buy_sell": r.get("buySell", "").strip(),
                "quantity": clean_number(r.get("quantityTraded")),
                "price": clean_number(r.get("tradePrice")),
            }
            for r in rows
        ]

    # --- holidays ---

    def holidays(self, holiday_type: str = "trading") -> list[dict]:
        data = self.fetch("/holiday-master", params={"type": holiday_type})
        # NSE returns dict keyed by segment codes (CM, FO, etc.)
        if not isinstance(data, dict):
            return []
        all_holidays: list[dict] = []
        for segment, entries in data.items():
            if not isinstance(entries, list):
                continue
            for r in entries:
                all_holidays.append(
                    {
                        "date": clean_date(r.get("tradingDate")),
                        "day": r.get("weekDay", "").strip(),
                        "description": r.get("description", "").strip(),
                        "segment": segment,
                    }
                )
        return all_holidays

    # --- index ---

    def index(self, name: str = "NIFTY 50") -> dict:
        data = self.fetch("/equity-stockIndices", params={"index": name})
        if not data or "error" in data:
            raise DataNotAvailable(f"Index not found: {name}")
        stocks = data.get("data", [])
        advance = data.get("advance", {})
        return {
            "name": name,
            "advance": clean_number(advance.get("advances")),
            "decline": clean_number(advance.get("declines")),
            "unchanged": clean_number(advance.get("unchanged")),
            "constituents": [
                {
                    "symbol": s.get("symbol", "").strip(),
                    "name": s.get("meta", {}).get("companyName", "")
                    if isinstance(s.get("meta"), dict)
                    else "",
                    "isin": s.get("meta", {}).get("isin", "")
                    if isinstance(s.get("meta"), dict)
                    else "",
                    "ltp": clean_number(s.get("lastPrice")),
                    "open": clean_number(s.get("open")),
                    "high": clean_number(s.get("dayHigh")),
                    "low": clean_number(s.get("dayLow")),
                    "prev_close": clean_number(s.get("previousClose")),
                    "change": clean_number(s.get("change")),
                    "pct_change": clean_number(s.get("pChange")),
                    "year_high": clean_number(s.get("yearHigh")),
                    "year_low": clean_number(s.get("yearLow")),
                    "ff_market_cap": clean_number(s.get("ffmc")),
                }
                for s in stocks
                if s.get("symbol") != name  # exclude the index row itself
            ],
        }

    # --- shareholding ---

    def shareholding(self, symbol: str) -> list[dict]:
        data = self.fetch("/corporateShareholding", params={"symbol": symbol.upper()})
        if not data:
            raise DataNotAvailable(f"No shareholding for {symbol}")
        rows = data if isinstance(data, list) else data.get("data", [])
        return [
            {
                "date": clean_date(r.get("date") or r.get("submissionDate")),
                "promoter_pct": clean_number(r.get("pr_and_prgrp")),
                "public_pct": clean_number(r.get("public_val")),
                "employee_trusts_pct": clean_number(r.get("employeeTrusts")),
            }
            for r in rows
        ]

    # --- status ---

    def status(self) -> list[dict]:
        data = self.fetch("/marketStatus")
        rows = data if isinstance(data, list) else data.get("marketState", [])
        return [
            {
                "market": r.get("market", "").strip(),
                "status": r.get("marketStatus", "").strip(),
                "index": r.get("index", "").strip(),
                "last": clean_number(r.get("last")),
                "change": clean_number(r.get("variation")),
                "pct_change": clean_number(r.get("percentChange")),
            }
            for r in rows
        ]

    # --- lookup ---

    def lookup(self, query: str) -> list[dict]:
        data = self.fetch("/search/autocomplete", params={"q": query})
        rows = data.get("symbols", []) if isinstance(data, dict) else []
        return [
            {
                "symbol": r.get("symbol", "").strip(),
                "name": r.get("symbol_info", "").strip(),
                "type": r.get("result_type", "").strip(),
            }
            for r in rows
        ]

    # --- gainers / losers (derived from index data) ---

    def gainers(self, index: str = "NIFTY 50", count: int = 10) -> list[dict]:
        idx = self.index(index)
        sorted_stocks = sorted(
            idx["constituents"],
            key=lambda s: s.get("pct_change") or 0,
            reverse=True,
        )
        return sorted_stocks[:count]

    def losers(self, index: str = "NIFTY 50", count: int = 10) -> list[dict]:
        idx = self.index(index)
        sorted_stocks = sorted(
            idx["constituents"],
            key=lambda s: s.get("pct_change") or 0,
        )
        return sorted_stocks[:count]

    # --- announcements ---

    def announcements(self, symbol: str | None = None) -> list[dict]:
        params: dict = {"index": "equities"}
        if symbol:
            params["symbol"] = symbol.upper()
        data = self.fetch("/corporate-announcements", params=params)
        rows = data if isinstance(data, list) else []
        return [
            {
                "symbol": r.get("symbol", "").strip(),
                "subject": r.get("subject", "").strip(),
                "date": clean_date(r.get("an_dt")),
                "broadcast_date": clean_date(r.get("broadcast_dt")),
                "description": r.get("desc", "").strip(),
            }
            for r in rows
        ]

    # --- advances (derived from index) ---

    def advances(self) -> dict:
        idx = self.index("NIFTY 50")
        return {
            "index": "NIFTY 50",
            "advances": idx["advance"],
            "declines": idx["decline"],
            "unchanged": idx["unchanged"],
        }
