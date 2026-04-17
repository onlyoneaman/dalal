"""dalal error hierarchy."""


class DalalError(Exception):
    """Base error for all dalal exceptions."""


class ExchangeError(DalalError):
    """Exchange returned an error response."""


class AuthError(ExchangeError):
    """Session or cookie expired."""


class SymbolNotFound(ExchangeError):
    """Invalid symbol or scripcode."""


class DataNotAvailable(ExchangeError):
    """Valid symbol but no data for the requested range."""


class NetworkError(DalalError):
    """Connection, timeout, or transport error."""


class RateLimited(NetworkError):
    """Too many requests — exchange is throttling."""


class ExchangeDown(NetworkError):
    """Exchange returned 503 or is under maintenance."""


class ValidationError(DalalError):
    """Invalid input parameters (bad date format, missing field, etc.)."""
