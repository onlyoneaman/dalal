"""NSESession tests — raw passthrough format."""

import responses
import pytest

from dalal.nse import NSESession
from dalal.errors import SymbolNotFound


class TestNSEQuote:
    @responses.activate
    def test_quote_returns_full_response(self):
        responses.add(responses.GET, "https://www.nseindia.com/option-chain", body="ok")
        responses.add(
            responses.GET,
            "https://www.nseindia.com/api/quote-equity",
            json={
                "info": {
                    "symbol": "RELIANCE",
                    "companyName": "Reliance Industries",
                    "isin": "INE002A01018",
                },
                "priceInfo": {
                    "lastPrice": 1365.10,
                    "vwap": 1358.5,
                    "lowerCP": "1215.00",
                },
                "industryInfo": {"sector": "Oil Gas"},
            },
        )
        nse = NSESession()
        result = nse.quote("RELIANCE")
        assert result["info"]["symbol"] == "RELIANCE"
        assert result["priceInfo"]["lastPrice"] == 1365.10
        assert result["priceInfo"]["vwap"] == 1358.5
        assert result["industryInfo"]["sector"] == "Oil Gas"
        nse.close()

    @responses.activate
    def test_quote_invalid_symbol(self):
        responses.add(responses.GET, "https://www.nseindia.com/option-chain", body="ok")
        responses.add(
            responses.GET,
            "https://www.nseindia.com/api/quote-equity",
            json={"error": "not found"},
        )
        nse = NSESession()
        with pytest.raises(SymbolNotFound):
            nse.quote("INVALID")
        nse.close()


class TestNSEHistory:
    @responses.activate
    def test_history_returns_raw_rows(self):
        responses.add(responses.GET, "https://www.nseindia.com/option-chain", body="ok")
        responses.add(
            responses.GET,
            "https://www.nseindia.com/api/NextApi/apiClient/GetQuoteApi",
            json=[
                {
                    "chClosingPrice": 1365,
                    "chTotTradedQty": 5000000,
                    "vwap": 1358.5,
                    "mtimestamp": "15-Apr-2025",
                }
            ],
        )
        nse = NSESession()
        result = nse.history("RELIANCE", "2025-04-01", "2025-04-15")
        assert len(result) == 1
        assert result[0]["chClosingPrice"] == 1365
        assert result[0]["vwap"] == 1358.5
        nse.close()


class TestNSEIndex:
    @responses.activate
    def test_index_returns_full_response(self):
        responses.add(responses.GET, "https://www.nseindia.com/option-chain", body="ok")
        responses.add(
            responses.GET,
            "https://www.nseindia.com/api/equity-stockIndices",
            json={
                "name": "NIFTY 50",
                "advance": {"advances": 30},
                "timestamp": "17-Apr-2026 16:00:00",
                "data": [
                    {
                        "symbol": "HDFCBANK",
                        "totalTradedVolume": 37282544,
                        "perChange365d": -16.09,
                    }
                ],
                "metadata": {"totalTradedValue": 353730230165.26},
            },
        )
        nse = NSESession()
        result = nse.index("NIFTY 50")
        assert result["advance"]["advances"] == 30
        assert result["timestamp"] == "17-Apr-2026 16:00:00"
        assert result["data"][0]["totalTradedVolume"] == 37282544
        assert result["metadata"]["totalTradedValue"] == 353730230165.26
        nse.close()
