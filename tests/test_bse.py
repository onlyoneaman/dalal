"""BSESession tests — raw passthrough format."""

import responses
import pytest

from dalal.bse import BSESession
from dalal.errors import SymbolNotFound


class TestBSEQuote:
    @responses.activate
    def test_quote_returns_full_response(self):
        responses.add(
            responses.GET,
            "https://api.bseindia.com/BseIndiaAPI/api/getScripHeaderData/w",
            json={
                "Header": {"PrevClose": "1350.00", "LTP": "1365.10", "High": "1370.00"},
                "CurrRate": {"Chg": "15.10", "PcChg": "1.12"},
                "Cmpname": {"FullN": "Reliance Industries Ltd."},
            },
        )
        bse = BSESession()
        result = bse.quote("500325")
        # Full response preserved
        assert result["Header"]["LTP"] == "1365.10"
        assert result["CurrRate"]["Chg"] == "15.10"
        assert result["Cmpname"]["FullN"] == "Reliance Industries Ltd."
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
    def test_fundamentals_returns_full_response(self):
        responses.add(
            responses.GET,
            "https://api.bseindia.com/BseIndiaAPI/api/TabResults_PAR/w",
            json={
                "col1": "(in Cr.)",
                "col2": "Dec-25",
                "col3": "Sep-25",
                "resultinCr": [
                    {"title": "Revenue", "v1": "1,25,741.00", "v2": "1,30,610.00"},
                ],
                "resultinM": [
                    {"title": "Revenue", "v1": "12,574.10", "v2": "13,061.00"},
                ],
            },
        )
        bse = BSESession()
        result = bse.fundamentals("500325")
        # Full response — both Cr and M preserved
        assert result["col1"] == "(in Cr.)"
        assert result["col2"] == "Dec-25"
        assert len(result["resultinCr"]) == 1
        assert len(result["resultinM"]) == 1
        assert result["resultinCr"][0]["v1"] == "1,25,741.00"
        bse.close()


class TestBSEMeta:
    @responses.activate
    def test_meta_returns_full_response(self):
        responses.add(
            responses.GET,
            "https://api.bseindia.com/BseIndiaAPI/api/ComHeadernew/w",
            json={
                "EPS": "35.21",
                "PE": "38.77",
                "ConEPS": "72.25",
                "ConPE": "18.89",
                "PB": "3.52",
                "ROE": "9.09",
                "Group": "A",
                "Industry": "Refineries",
                "FaceVal": "10",
                "ISIN": "INE002A01018",
            },
        )
        bse = BSESession()
        result = bse.meta("500325")
        # Full response — all fields preserved including Group (was buggy before)
        assert result["ConPE"] == "18.89"
        assert result["Group"] == "A"
        assert result["FaceVal"] == "10"
        assert result["Industry"] == "Refineries"
        bse.close()
