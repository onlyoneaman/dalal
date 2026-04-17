"""Exchange base class — session management, rate limiting, HTTP fetch."""

from __future__ import annotations

import time

import requests

from dalal.errors import (
    AuthError,
    DalalError,
    ExchangeDown,
    ExchangeError,
    NetworkError,
    RateLimited,
)


class Exchange:
    """Base class for NSE and BSE session handlers.

    Subclasses set BASE_URL, RATE_LIMIT, TIMEOUT and override _init_session().
    """

    BASE_URL: str = ""
    RATE_LIMIT: int = 3  # requests per second
    TIMEOUT: int = 15

    # HTTP status → exception mapping
    _STATUS_MAP: dict[int, type[DalalError]] = {
        401: AuthError,
        403: AuthError,
        429: RateLimited,
        503: ExchangeDown,
        502: ExchangeDown,
    }

    def __init__(self):
        self._session = requests.Session()
        self._last_request_time: float = 0.0
        self._min_interval: float = 1.0 / self.RATE_LIMIT
        self._init_session()

    def _init_session(self) -> None:
        """Subclasses override to set headers, prime cookies, etc."""

    def _throttle(self) -> None:
        """Enforce rate limit by sleeping if needed."""
        now = time.monotonic()
        elapsed = now - self._last_request_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request_time = time.monotonic()

    def fetch(self, path: str, params: dict | None = None) -> dict | list:
        """GET a JSON endpoint. Throttles, maps errors, returns parsed JSON."""
        self._throttle()
        url = f"{self.BASE_URL}{path}" if not path.startswith("http") else path
        try:
            resp = self._session.get(url, params=params, timeout=self.TIMEOUT)
        except requests.ConnectionError as e:
            raise NetworkError(f"Connection failed: {e}") from e
        except requests.Timeout as e:
            raise NetworkError(f"Request timed out: {e}") from e

        exc_class = self._STATUS_MAP.get(resp.status_code)
        if exc_class:
            raise exc_class(f"HTTP {resp.status_code}: {resp.text[:200]}")

        if resp.status_code >= 400:
            raise ExchangeError(f"HTTP {resp.status_code}: {resp.text[:200]}")

        try:
            return resp.json()
        except ValueError:
            # Some endpoints return empty or HTML on "no data"
            return {}

    def close(self) -> None:
        """Close the underlying requests session."""
        self._session.close()
