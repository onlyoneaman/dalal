"""BSE exchange session — all BSE API endpoint implementations."""

from __future__ import annotations

from dalal.base import Exchange
from dalal.constants import BSE_API, BSE_HEADERS, BSE_RATE_LIMIT, BSE_TIMEOUT
from dalal.errors import DataNotAvailable, SymbolNotFound
from dalal.utils import clean_date, clean_number


class BSESession(Exchange):
    BASE_URL = BSE_API
    RATE_LIMIT = BSE_RATE_LIMIT
    TIMEOUT = BSE_TIMEOUT

    def _init_session(self) -> None:
        self._session.headers.update(BSE_HEADERS)

    # --- quote ---

    def quote(self, scripcode: str) -> dict:
        data = self.fetch(
            "/getScripHeaderData/w", params={"Ession": "E", "scripcode": scripcode}
        )
        header = data.get("Header", {})
        if not header:
            raise SymbolNotFound(f"BSE scripcode not found: {scripcode}")
        return {
            "prev_close": clean_number(header.get("PrevClose")),
            "open": clean_number(header.get("Open")),
            "high": clean_number(header.get("High")),
            "low": clean_number(header.get("Low")),
            "ltp": clean_number(header.get("LTP")),
            "scripcode": scripcode,
        }

    # --- actions ---

    def actions(self, scripcode: str | None = None) -> list[dict]:
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
        table = data.get("Table", [])
        return [
            {
                "scripcode": r.get("scrip_code", "").strip(),
                "name": r.get("short_name", "").strip(),
                "long_name": r.get("long_name", "").strip(),
                "ex_date": clean_date(r.get("exdate") or r.get("Ex_date")),
                "purpose": r.get("Purpose", "").strip(),
                "record_date": clean_date(r.get("RD_Date")),
                "payment_date": clean_date(r.get("payment_date")),
            }
            for r in table
        ]

    # --- fundamentals ---

    def fundamentals(self, scripcode: str) -> dict:
        import json as _json

        data = self.fetch(
            "/TabResults_PAR/w",
            params={"scripcode": scripcode, "tabtype": "RESULTS"},
        )
        # BSE returns a JSON string that needs double-parsing
        if isinstance(data, str):
            try:
                data = _json.loads(data)
            except (ValueError, TypeError):
                pass
        if not data or not isinstance(data, dict):
            raise DataNotAvailable(f"No fundamentals for BSE {scripcode}")

        currency_unit = data.get("col1", "").strip("() ")
        periods = [data.get(f"col{i}", "") for i in range(2, 5) if data.get(f"col{i}")]

        results_raw = data.get("resultinCr", [])
        results = []
        for item in results_raw:
            title = item.get("title", "")
            values = [clean_number(item.get(f"v{i}")) for i in range(1, 4)]
            for i, period in enumerate(periods):
                if i >= len(values):
                    break
                # Build per-period dict lazily
                if i >= len(results):
                    results.append({"period": period})
                results[i][title.lower().replace(" ", "_").replace("%", "pct")] = (
                    values[i]
                )

        return {
            "scripcode": scripcode,
            "currency_unit": currency_unit,
            "periods": results,
        }

    # --- meta ---

    def meta(self, scripcode: str) -> dict:
        data = self.fetch("/ComHeadernew/w", params={"scripcode": scripcode})
        if not data:
            raise DataNotAvailable(f"No meta for BSE {scripcode}")
        return {
            "scripcode": scripcode,
            "eps": clean_number(data.get("EPS")),
            "pe": clean_number(data.get("PE")),
            "con_eps": clean_number(data.get("ConEPS")),
            "con_pe": clean_number(data.get("ConPE")),
            "pb": clean_number(data.get("PB")),
            "roe": clean_number(data.get("ROE")),
            "opm": clean_number(data.get("OPM")),
            "npm": clean_number(data.get("NPM")),
            "isin": data.get("ISIN"),
            "industry": data.get("Industry"),
            "group": data.get("Scrip_group"),
        }

    # --- result_calendar ---

    def result_calendar(self, scripcode: str | None = None) -> list[dict]:
        params: dict = {}
        if scripcode:
            params["scripcode"] = scripcode
        data = self.fetch("/Corpforthresults/w", params=params)
        table = data.get("Table", [])
        return [
            {
                "scripcode": r.get("scrip_Code", "").strip(),
                "name": r.get("short_name", "").strip(),
                "long_name": r.get("Long_Name", "").strip(),
                "meeting_date": clean_date(r.get("meeting_date")),
            }
            for r in table
        ]

    # --- gainers ---

    def gainers(self, by: str = "group", name: str = "A") -> list[dict]:
        return self._movers("G", by, name)

    # --- losers ---

    def losers(self, by: str = "group", name: str = "A") -> list[dict]:
        return self._movers("L", by, name)

    def _movers(self, gl_type: str, by: str, name: str) -> list[dict]:
        params = {
            "GLession": gl_type,
            "reqtype": by,
            "sess": name,
            "Ession1": "",
        }
        data = self.fetch("/MktRGainerLoserData/w", params=params)
        table = data.get("Table", [])
        return [
            {
                "scripcode": r.get("scrip_cd", "").strip(),
                "name": r.get("scrip_nm", "").strip(),
                "ltp": clean_number(r.get("ltradert")),
                "change": clean_number(r.get("change")),
                "pct_change": clean_number(r.get("pctchange")),
            }
            for r in table
        ]

    # --- announcements ---

    def announcements(
        self,
        scripcode: str | None = None,
        page: int = 1,
    ) -> list[dict]:
        params: dict = {"pageNo": str(page), "strSearch": ""}
        if scripcode:
            params["scripcode"] = scripcode
        data = self.fetch("/AnnSubCategoryGetData/w", params=params)
        table = data.get("Table", [])
        return [
            {
                "scripcode": r.get("SCRIP_CD", "").strip(),
                "name": r.get("SLONGNAME", "").strip(),
                "headline": r.get("HEADLINE", "").strip(),
                "date": clean_date(r.get("DT_TM")),
                "attachment_url": r.get("ATTACHMENTNAME", ""),
            }
            for r in table
        ]

    # --- status (advance/decline) ---

    def status(self) -> list[dict]:
        data = self.fetch("/advanceDecline/w")
        table = data if isinstance(data, list) else data.get("Table", [])
        return [
            {
                "index": r.get("indx_nm", "").strip(),
                "advances": clean_number(r.get("adv")),
                "declines": clean_number(r.get("dec")),
                "unchanged": clean_number(r.get("unc")),
            }
            for r in table
        ]

    # --- lookup ---

    def lookup(self, query: str) -> list[dict]:
        data = self.fetch(
            "/PeerSmartSearch/w",
            params={"Type": "S", "text": query},
        )
        # BSE returns HTML fragment — parse it
        if isinstance(data, str) or not data:
            return []
        # If API returns a list directly
        if isinstance(data, list):
            return [
                {
                    "scripcode": str(r.get("scrip_cd", "")).strip(),
                    "name": r.get("scrip_nm", "").strip(),
                }
                for r in data
            ]
        return []
