"""dalal — Unified Python API for Indian stock exchanges (NSE + BSE).

Usage::

    import dalal

    dalal.quote("RELIANCE")
    dalal.fundamentals("500325")
    dalal.actions("RELIANCE")
"""

from dalal.dalal import Dalal
from dalal.errors import (
    AuthError,
    DalalError,
    DataNotAvailable,
    ExchangeDown,
    ExchangeError,
    NetworkError,
    RateLimited,
    SymbolNotFound,
    ValidationError,
)

# Shared instance — lazy sessions, created on first use
_default = Dalal()

# Module-level functions delegating to the shared instance
quote = _default.quote
history = _default.history
actions = _default.actions
fundamentals = _default.fundamentals
meta = _default.meta
index = _default.index
holidays = _default.holidays
bulk_deals = _default.bulk_deals
block_deals = _default.block_deals
shareholding = _default.shareholding
gainers = _default.gainers
losers = _default.losers
announcements = _default.announcements
status = _default.status
lookup = _default.lookup
result_calendar = _default.result_calendar
advances = _default.advances

__all__ = [
    "Dalal",
    "quote",
    "history",
    "actions",
    "fundamentals",
    "meta",
    "index",
    "holidays",
    "bulk_deals",
    "block_deals",
    "shareholding",
    "gainers",
    "losers",
    "announcements",
    "status",
    "lookup",
    "result_calendar",
    "advances",
    "DalalError",
    "ExchangeError",
    "AuthError",
    "SymbolNotFound",
    "DataNotAvailable",
    "NetworkError",
    "RateLimited",
    "ExchangeDown",
    "ValidationError",
]
