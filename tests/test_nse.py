"""NSESession tests — unit tests with mocked HTTP."""

import responses
import pytest

from dalal.nse import NSESession
from dalal.errors import SymbolNotFound


class TestNSEQuote:
    @responses.activate
    def test_quote_returns_fields(self):
        # Cookie priming
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
                    "open": 1360.0,
                    "previousClose": 1350.0,
                    "change": 15.10,
                    "pChange": 1.12,
                    "intraDayHighLow": {"max": 1370.0, "min": 1340.0},
                    "weekHighLow": {"max": 1600.0, "min": 1200.0},
                },
            },
        )
        nse = NSESession()
        result = nse.quote("RELIANCE")
        assert result["symbol"] == "RELIANCE"
        assert result["ltp"] == 1365.10
        assert result["year_high"] == 1600.0
        nse.close()

    @responses.activate
    def test_quote_invalid_symbol(self):
        responses.add(responses.GET, "https://www.nseindia.com/option-chain", body="ok")
        responses.add(
            responses.GET,
            "https://www.nseindia.com/api/quote-equity",
            json={"error": "symbol not found"},
        )
        nse = NSESession()
        with pytest.raises(SymbolNotFound):
            nse.quote("INVALID")
        nse.close()


class TestNSEHistory:
    @responses.activate
    def test_history_returns_ohlcv(self):
        responses.add(responses.GET, "https://www.nseindia.com/option-chain", body="ok")
        responses.add(
            responses.GET,
            "https://www.nseindia.com/api/historical/cm/equity",
            json={
                "data": [
                    {
                        "CH_TIMESTAMP": "2025-04-01",
                        "CH_OPENING_PRICE": "1350",
                        "CH_TRADE_HIGH_PRICE": "1370",
                        "CH_TRADE_LOW_PRICE": "1340",
                        "CH_CLOSING_PRICE": "1365",
                        "CH_TOT_TRADED_QTY": "5000000",
                    }
                ]
            },
        )
        nse = NSESession()
        result = nse.history("RELIANCE", "2025-04-01", "2025-04-15")
        assert len(result) == 1
        assert result[0]["close"] == 1365.0
        assert result[0]["volume"] == 5000000.0
        nse.close()
