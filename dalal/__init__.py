"""dalal — Unified Python API for Indian stock exchanges (NSE + BSE)."""

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

__all__ = [
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
