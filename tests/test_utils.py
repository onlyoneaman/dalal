from datetime import date

import pytest

from dalal.utils import (
    chunk_dates,
    clean_date,
    clean_number,
    fmt_date_dmy,
    parse_date,
)


def test_parse_date_iso():
    assert parse_date("2025-01-15") == date(2025, 1, 15)


def test_parse_date_dmy():
    assert parse_date("15-01-2025") == date(2025, 1, 15)


def test_parse_date_object():
    d = date(2025, 1, 15)
    assert parse_date(d) is d


def test_parse_date_invalid():
    with pytest.raises(ValueError, match="Cannot parse date"):
        parse_date("not-a-date")


def test_fmt_date_dmy():
    assert fmt_date_dmy(date(2025, 1, 5)) == "05-01-2025"


def test_clean_number_int():
    assert clean_number(42) == 42.0


def test_clean_number_comma():
    assert clean_number("1,23,456.78") == 123456.78


def test_clean_number_none():
    assert clean_number(None) is None
    assert clean_number("—") is None
    assert clean_number("") is None
    assert clean_number("NA") is None


def test_clean_date_iso():
    assert clean_date("15-01-2025") == "2025-01-15"


def test_clean_date_empty():
    assert clean_date(None) is None
    assert clean_date("") is None


def test_chunk_dates_short():
    chunks = chunk_dates(date(2025, 1, 1), date(2025, 2, 19))
    assert len(chunks) == 1


def test_chunk_dates_long():
    chunks = chunk_dates(date(2025, 1, 1), date(2025, 12, 31))
    assert len(chunks) == 4
    assert chunks[0][0] == date(2025, 1, 1)
    assert chunks[-1][1] == date(2025, 12, 31)
