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
        responses.add(
            responses.GET,
            "https://api.bseindia.com/BseIndiaAPI/api/TabResults_PAR/w",
            json={
                "currency_unit": "Cr",
                "periods": ["Dec-25", "Sep-25"],
                "results_in_crores": {
                    "Dec-25": {
                        "Revenue": "1,25,741",
                        "Net Profit": "9,396",
                        "EPS": "6.94",
                    },
                    "Sep-25": {
                        "Revenue": "1,30,610",
                        "Net Profit": "9,129",
                        "EPS": "6.75",
                    },
                },
            },
        )
        bse = BSESession()
        result = bse.fundamentals("500325")
        assert len(result["periods"]) == 2
        assert result["periods"][0]["revenue"] == 125741.0
        assert result["periods"][0]["eps"] == 6.94
        bse.close()
