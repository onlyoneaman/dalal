"""BSESession tests — unit tests with mocked HTTP."""

import responses
import pytest

from dalal.bse import BSESession
from dalal.errors import SymbolNotFound


class TestBSEQuote:
    @responses.activate
    def test_quote_returns_ohlc(self):
        responses.add(
            responses.GET,
            "https://api.bseindia.com/BseIndiaAPI/api/getScripHeaderData/w",
            json={
                "Header": {
                    "PrevClose": "1350.00",
                    "Open": "1355.00",
                    "High": "1370.00",
                    "Low": "1340.00",
                    "LTP": "1365.10",
                }
            },
        )
        bse = BSESession()
        result = bse.quote("500325")
        assert result["ltp"] == 1365.10
        assert result["high"] == 1370.0
        assert result["scripcode"] == "500325"
        bse.close()

    @responses.activate
    def test_quote_invalid_scripcode(self):
        responses.add(
            responses.GET,
            "https://api.bseindia.com/BseIndiaAPI/api/getScripHeaderData/w",
            json={"Header": {}},
        )
        bse = BSESession()
        with pytest.raises(SymbolNotFound):
            bse.quote("999999")
        bse.close()


class TestBSEFundamentals:
    @responses.activate
    def test_fundamentals_returns_periods(self):
        # Mock the actual BSE response format: col1-col4 + resultinCr
        responses.add(
            responses.GET,
            "https://api.bseindia.com/BseIndiaAPI/api/TabResults_PAR/w",
            json={
                "col1": "(in Cr.)",
                "col2": "Dec-25",
                "col3": "Sep-25",
                "resultinCr": [
                    {"title": "Revenue", "v1": "1,25,741.00", "v2": "1,30,610.00"},
                    {"title": "Net Profit", "v1": "9,396.00", "v2": "9,129.00"},
                    {"title": "EPS", "v1": "6.94", "v2": "6.75"},
                ],
            },
        )
        bse = BSESession()
        result = bse.fundamentals("500325")
        assert len(result["periods"]) == 2
        assert result["periods"][0]["revenue"] == 125741.0
        assert result["periods"][0]["eps"] == 6.94
        assert result["periods"][1]["net_profit"] == 9129.0
        assert result["currency_unit"] == "in Cr."
        bse.close()
