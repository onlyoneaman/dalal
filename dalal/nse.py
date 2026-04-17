"""NSE exchange session — cookie-primed session, all NSE endpoint implementations.

All methods return the raw API response with minimal transformation:
- String values are stripped
- Structure is preserved as-is
- If NSE adds new fields, they flow through automatically
"""

from __future__ import annotations

from datetime import date

from dalal.base import Exchange
from dalal.constants import (
    NSE_API,
    NSE_COOKIE_URL,
    NSE_HEADERS,
    NSE_RATE_LIMIT,
    NSE_TIMEOUT,
)
from dalal.errors import AuthError, DataNotAvailable, SymbolNotFound
from dalal.utils import chunk_dates, fmt_date_dmy, parse_date


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
            self._cookies_primed = False
            self._prime_cookies()
            return super().fetch(path, params)

    # --- quote ---

    def quote(self, symbol: str) -> dict:
        """Full equity quote — returns the entire NSE response.

        Includes: info, metadata, securityInfo, priceInfo, industryInfo,
        preOpenMarket, sddDetails.
        """
        data = self.fetch("/quote-equity", params={"symbol": symbol.upper()})
        if not data or "error" in data:
            raise SymbolNotFound(f"NSE symbol not found: {symbol}")
        return data

    # --- history ---

    def history(
        self,
        symbol: str,
        start: str | date,
        end: str | date,
        series: str = "EQ",
    ) -> list[dict]:
        """Historical OHLCV — auto-chunks into 100-day windows.

        NOTE: NSE endpoint /historical/cm/equity may return 404.
        If so, this method raises ExchangeError.
        """
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
            all_rows.extend(data.get("data", []))
        return all_rows

    # --- actions ---

    def actions(self, symbol: str | None = None) -> list[dict]:
        """Corporate actions — dividends, splits, bonuses.

        Returns raw list from NSE with all fields.
        """
        params: dict = {"index": "equities"}
        if symbol:
            params["symbol"] = symbol.upper()
        data = self.fetch("/corporates-corporateActions", params=params)
        return data if isinstance(data, list) else []

    # --- bulk_deals ---

    def bulk_deals(self, start: str | date, end: str | date) -> list[dict]:
        """Historical bulk deals.

        NOTE: NSE endpoint /historical/bulk-deals may return 404.
        """
        params = {
            "from": fmt_date_dmy(parse_date(start)),
            "to": fmt_date_dmy(parse_date(end)),
        }
        data = self.fetch("/historical/bulk-deals", params=params)
        if isinstance(data, dict):
            return data.get("data", [])
        return data if isinstance(data, list) else []

    # --- block_deals ---

    def block_deals(self) -> dict:
        """Block deals — returns full response including session stats and market status."""
        data = self.fetch("/block-deal")
        return data if isinstance(data, dict) else {"data": []}

    # --- holidays ---

    def holidays(self, holiday_type: str = "trading") -> dict:
        """Trading/clearing holidays — returns dict keyed by segment (CM, FO, etc.)."""
        data = self.fetch("/holiday-master", params={"type": holiday_type})
        return data if isinstance(data, dict) else {}

    # --- index ---

    def index(self, name: str = "NIFTY 50") -> dict:
        """Index constituents with live prices — returns full response.

        Includes: data (constituents), advance, timestamp, metadata, marketStatus.
        """
        data = self.fetch("/equity-stockIndices", params={"index": name})
        if not data or "error" in data:
            raise DataNotAvailable(f"Index not found: {name}")
        return data

    # --- shareholding ---

    def shareholding(self, symbol: str) -> dict | list:
        """Shareholding pattern.

        NOTE: NSE endpoint /corporateShareholding may return 404.
        """
        data = self.fetch("/corporateShareholding", params={"symbol": symbol.upper()})
        if not data:
            raise DataNotAvailable(f"No shareholding for {symbol}")
        return data

    # --- status ---

    def status(self) -> dict:
        """Market status — returns full response.

        Includes: marketState, marketcap, indicativenifty50, giftnifty.
        """
        data = self.fetch("/marketStatus")
        return data if isinstance(data, dict) else {"marketState": []}

    # --- lookup ---

    def lookup(self, query: str) -> dict:
        """Symbol search — returns full response.

        Includes: symbols, mfsymbols, search_content, sitemap.
        """
        data = self.fetch("/search/autocomplete", params={"q": query})
        return data if isinstance(data, dict) else {"symbols": []}

    # --- announcements ---

    def announcements(self, symbol: str | None = None) -> list[dict]:
        """Corporate announcements — returns raw list with all fields."""
        params: dict = {"index": "equities"}
        if symbol:
            params["symbol"] = symbol.upper()
        data = self.fetch("/corporate-announcements", params=params)
        return data if isinstance(data, list) else []

    # --- convenience methods (derived from raw data) ---

    def gainers(self, index: str = "NIFTY 50", count: int = 10) -> list[dict]:
        """Top gainers by pct_change from index constituents."""
        idx = self.index(index)
        stocks = [s for s in idx.get("data", []) if s.get("symbol") != index]
        return sorted(stocks, key=lambda s: s.get("pChange") or 0, reverse=True)[:count]

    def losers(self, index: str = "NIFTY 50", count: int = 10) -> list[dict]:
        """Top losers by pct_change from index constituents."""
        idx = self.index(index)
        stocks = [s for s in idx.get("data", []) if s.get("symbol") != index]
        return sorted(stocks, key=lambda s: s.get("pChange") or 0)[:count]

    def advances(self) -> dict:
        """Advance/decline from NIFTY 50 index data."""
        idx = self.index("NIFTY 50")
        return idx.get("advance", {})
