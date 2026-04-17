"""Dalal public API tests."""

import pytest
import responses

from dalal import Dalal, ValidationError


class TestDalalRouting:
    def test_invalid_exchange_raises(self):
        d = Dalal()
        with pytest.raises(ValidationError, match="Invalid exchange"):
            d.quote("X", exchange="NASDAQ")
        d.close()

    def test_context_manager(self):
        with Dalal() as d:
            assert d._nse is None  # lazy — not initialized yet
            assert d._bse is None

    @responses.activate
    def test_quote_nse_default(self):
        responses.add(responses.GET, "https://www.nseindia.com/option-chain", body="ok")
        responses.add(
            responses.GET,
            "https://www.nseindia.com/api/quote-equity",
            json={
                "info": {
                    "symbol": "RELIANCE",
                    "companyName": "Reliance",
                    "isin": "INE002A01018",
                },
                "priceInfo": {
                    "lastPrice": 1365.0,
                    "open": 1360.0,
                    "previousClose": 1350.0,
                    "intraDayHighLow": {},
                    "weekHighLow": {},
                },
            },
        )
        with Dalal() as d:
            result = d.quote("RELIANCE")
            assert result["ltp"] == 1365.0
            assert d._nse is not None  # lazy init happened
            assert d._bse is None  # BSE not touched

    @responses.activate
    def test_quote_bse_explicit(self):
        responses.add(
            responses.GET,
            "https://api.bseindia.com/BseIndiaAPI/api/getScripHeaderData/w",
            json={
                "Header": {
                    "LTP": "1365.10",
                    "Open": "1360",
                    "High": "1370",
                    "Low": "1340",
                    "PrevClose": "1350",
                }
            },
        )
        with Dalal() as d:
            result = d.quote("500325", exchange="BSE")
            assert result["ltp"] == 1365.10
            assert d._bse is not None
            assert d._nse is None  # NSE not touched

    @responses.activate
    def test_fundamentals_uses_bse(self):
        responses.add(
            responses.GET,
            "https://api.bseindia.com/BseIndiaAPI/api/TabResults_PAR/w",
            json={
                "col1": "(in Cr.)",
                "col2": "Dec-25",
                "resultinCr": [
                    {"title": "Revenue", "v1": "100"},
                    {"title": "EPS", "v1": "5.0"},
                ],
            },
        )
        with Dalal() as d:
            result = d.fundamentals("500325")
            assert result["periods"][0]["revenue"] == 100.0
