"""Dalal public API tests — raw passthrough."""

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
            assert d._nse is None
            assert d._bse is None

    @responses.activate
    def test_quote_nse_default(self):
        responses.add(responses.GET, "https://www.nseindia.com/option-chain", body="ok")
        responses.add(
            responses.GET,
            "https://www.nseindia.com/api/quote-equity",
            json={
                "info": {"symbol": "RELIANCE"},
                "priceInfo": {"lastPrice": 1365.0},
            },
        )
        with Dalal() as d:
            result = d.quote("RELIANCE")
            assert result["priceInfo"]["lastPrice"] == 1365.0
            assert d._nse is not None
            assert d._bse is None

    @responses.activate
    def test_quote_bse_explicit(self):
        responses.add(
            responses.GET,
            "https://api.bseindia.com/BseIndiaAPI/api/getScripHeaderData/w",
            json={"Header": {"LTP": "1365.10"}},
        )
        with Dalal() as d:
            result = d.quote("500325", exchange="BSE")
            assert result["Header"]["LTP"] == "1365.10"
            assert d._bse is not None
            assert d._nse is None

    @responses.activate
    def test_fundamentals_uses_bse(self):
        responses.add(
            responses.GET,
            "https://api.bseindia.com/BseIndiaAPI/api/TabResults_PAR/w",
            json={
                "col1": "(in Cr.)",
                "col2": "Dec-25",
                "resultinCr": [{"title": "Revenue", "v1": "100"}],
            },
        )
        with Dalal() as d:
            result = d.fundamentals("500325")
            assert result["col1"] == "(in Cr.)"
            assert result["resultinCr"][0]["v1"] == "100"
