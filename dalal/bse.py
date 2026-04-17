"""BSE exchange session — all BSE API endpoint implementations.

All methods return the raw API response with minimal transformation:
- JSON strings are double-parsed where BSE wraps JSON in quotes
- Structure is preserved as-is
- If BSE adds new fields, they flow through automatically
"""

from __future__ import annotations

import json as _json

from dalal.base import Exchange
from dalal.constants import BSE_API, BSE_HEADERS, BSE_RATE_LIMIT, BSE_TIMEOUT
from dalal.errors import DataNotAvailable, SymbolNotFound


class BSESession(Exchange):
    BASE_URL = BSE_API
    RATE_LIMIT = BSE_RATE_LIMIT
    TIMEOUT = BSE_TIMEOUT

    def _init_session(self) -> None:
        self._session.headers.update(BSE_HEADERS)

    # --- quote ---

    def quote(self, scripcode: str) -> dict:
        """Full scrip quote — returns the entire BSE response.

        Includes: Header, CurrRate, Cmpname, CompResp.
        """
        data = self.fetch(
            "/getScripHeaderData/w", params={"Ession": "E", "scripcode": scripcode}
        )
        if not data or not data.get("Header"):
            raise SymbolNotFound(f"BSE scripcode not found: {scripcode}")
        return data

    # --- actions ---

    def actions(self, scripcode: str | None = None) -> list[dict]:
        """Corporate actions — returns raw Table list with all fields."""
        params = {
            "Type": "N",
            "Atea": "E",
            "mode": "",
            "Atea1": "",
            "DDession": "",
            "Ession": "",
            "Ession1": "",
            "strSearch": "",
            "FOession": "",
            "Ession2": "E",
        }
        if scripcode:
            params["scripcode"] = scripcode
        data = self.fetch("/DefaultData/w", params=params)
        return data.get("Table", []) if isinstance(data, dict) else []

    # --- fundamentals ---

    def fundamentals(self, scripcode: str) -> dict:
        """Results snapshot — returns full response with all result sets.

        BSE sometimes wraps JSON in quotes, so double-parse if needed.
        Includes: col1-col4, resultinCr, resultinM, resultinS.
        """
        data = self.fetch(
            "/TabResults_PAR/w",
            params={"scripcode": scripcode, "tabtype": "RESULTS"},
        )
        if isinstance(data, str):
            try:
                data = _json.loads(data)
            except (ValueError, TypeError):
                pass
        if not data or not isinstance(data, dict):
            raise DataNotAvailable(f"No fundamentals for BSE {scripcode}")
        return data

    # --- meta ---

    def meta(self, scripcode: str) -> dict:
        """Equity meta — returns full response with all fields.

        Includes: EPS, PE, ConEPS, ConPE, PB, ROE, OPM, NPM, CEPS,
        ConCEPS, ConOPM, ConNPM, ConPB, ConROE, FaceVal, ISIN,
        Industry, Sector, IndustryNew, Group, COName, etc.
        """
        data = self.fetch("/ComHeadernew/w", params={"scripcode": scripcode})
        if not data:
            raise DataNotAvailable(f"No meta for BSE {scripcode}")
        return data if isinstance(data, dict) else {}

    # --- result_calendar ---

    def result_calendar(self, scripcode: str | None = None) -> dict:
        """Upcoming earnings dates — returns full response."""
        params: dict = {}
        if scripcode:
            params["scripcode"] = scripcode
        data = self.fetch("/Corpforthresults/w", params=params)
        return data if isinstance(data, dict) else {}

    # --- gainers ---

    def gainers(self, by: str = "group", name: str = "A") -> list[dict]:
        """Top gainers — returns raw Table list with all fields."""
        return self._movers("G", by, name)

    # --- losers ---

    def losers(self, by: str = "group", name: str = "A") -> list[dict]:
        """Top losers — returns raw Table list with all fields."""
        return self._movers("L", by, name)

    def _movers(self, gl_type: str, by: str, name: str) -> list[dict]:
        params = {
            "GLession": gl_type,
            "reqtype": by,
            "sess": name,
            "Ession1": "",
        }
        data = self.fetch("/MktRGainerLoserData/w", params=params)
        return data.get("Table", []) if isinstance(data, dict) else []

    # --- announcements ---

    def announcements(
        self,
        scripcode: str | None = None,
        page: int = 1,
    ) -> dict:
        """Corporate announcements — returns full response."""
        params: dict = {"pageNo": str(page), "strSearch": ""}
        if scripcode:
            params["scripcode"] = scripcode
        data = self.fetch("/AnnSubCategoryGetData/w", params=params)
        return data if isinstance(data, dict) else {}

    # --- status (advance/decline) ---

    def status(self) -> list | dict:
        """Advance/decline for all indices — returns raw response."""
        return self.fetch("/advanceDecline/w")

    # --- lookup ---

    def lookup(self, query: str) -> list | dict:
        """Symbol search — returns raw response."""
        data = self.fetch(
            "/PeerSmartSearch/w",
            params={"Type": "S", "text": query},
        )
        return data if data else []
