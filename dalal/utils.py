"""Date parsing and number cleaning helpers."""

from __future__ import annotations

from datetime import date, datetime, timedelta


def parse_date(d: str | date | datetime) -> date:
    """Normalize a date input to a datetime.date.

    Accepts: "2025-01-15", "15-01-2025", date, datetime objects.
    """
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, date):
        return d
    d = d.strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d-%b-%Y", "%d %b %Y"):
        try:
            return datetime.strptime(d, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {d!r}")


def fmt_date_dmy(d: date) -> str:
    """Format date as DD-MM-YYYY (NSE format)."""
    return d.strftime("%d-%m-%Y")


def fmt_date_iso(d: date) -> str:
    """Format date as YYYY-MM-DD (ISO)."""
    return d.isoformat()


def clean_number(value: str | int | float | None) -> float | None:
    """Parse a number from exchange responses.

    Handles: commas, Indian formatting, trailing whitespace, "—", "-", "".
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    value = value.strip().replace(",", "")
    if not value or value in ("—", "-", "NA", "N/A"):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def clean_date(value: str | None) -> str | None:
    """Parse a date string from exchange responses and return ISO format."""
    if not value or not value.strip():
        return None
    try:
        return parse_date(value).isoformat()
    except ValueError:
        return None


def clean_row(raw: dict, renames: dict | None = None) -> dict:
    """Clean a raw API response row — pass everything through.

    - Renames known keys via renames map (old_key → new_key)
    - Cleans number-like values via clean_number
    - Strips string values
    - Passes unknown keys through untouched
    """
    renames = renames or {}
    out = {}
    for k, v in raw.items():
        key = renames.get(k, k)
        if isinstance(v, str):
            v = v.strip()
        out[key] = v
    return out


def chunk_dates(
    start: date, end: date, chunk_days: int = 100
) -> list[tuple[date, date]]:
    """Split a date range into chunks of chunk_days.

    NSE limits historical data to 100-day windows per request.
    """
    chunks = []
    current = start
    while current <= end:
        chunk_end = min(current + timedelta(days=chunk_days - 1), end)
        chunks.append((current, chunk_end))
        current = chunk_end + timedelta(days=1)
    return chunks
