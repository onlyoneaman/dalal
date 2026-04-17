import time

import pytest
import responses

from dalal.base import Exchange
from dalal.errors import (
    AuthError,
    ExchangeDown,
    ExchangeError,
    NetworkError,
    RateLimited,
)


class DummyExchange(Exchange):
    BASE_URL = "https://example.com"
    RATE_LIMIT = 100  # high limit for fast tests

    def _init_session(self):
        self._session.headers.update({"User-Agent": "test"})


class TestThrottle:
    def test_throttle_enforces_delay(self):
        ex = DummyExchange()
        ex.RATE_LIMIT = 5  # 5 req/s = 200ms between
        ex._min_interval = 1.0 / 5
        t1 = time.monotonic()
        ex._throttle()
        ex._throttle()
        elapsed = time.monotonic() - t1
        assert elapsed >= 0.15
        ex.close()


class TestErrorMapping:
    @responses.activate
    def test_401_raises_auth_error(self):
        responses.add(responses.GET, "https://example.com/test", status=401)
        ex = DummyExchange()
        with pytest.raises(AuthError):
            ex.fetch("/test")
        ex.close()

    @responses.activate
    def test_429_raises_rate_limited(self):
        responses.add(responses.GET, "https://example.com/test", status=429)
        ex = DummyExchange()
        with pytest.raises(RateLimited):
            ex.fetch("/test")
        ex.close()

    @responses.activate
    def test_503_raises_exchange_down(self):
        responses.add(responses.GET, "https://example.com/test", status=503)
        ex = DummyExchange()
        with pytest.raises(ExchangeDown):
            ex.fetch("/test")
        ex.close()

    @responses.activate
    def test_200_returns_json(self):
        responses.add(
            responses.GET,
            "https://example.com/test",
            json={"key": "value"},
            status=200,
        )
        ex = DummyExchange()
        result = ex.fetch("/test")
        assert result == {"key": "value"}
        ex.close()

    @responses.activate
    def test_404_raises_exchange_error(self):
        responses.add(responses.GET, "https://example.com/test", status=404)
        ex = DummyExchange()
        with pytest.raises(ExchangeError):
            ex.fetch("/test")
        ex.close()

    @responses.activate
    def test_empty_response_returns_dict(self):
        responses.add(
            responses.GET,
            "https://example.com/test",
            body="not json",
            status=200,
        )
        ex = DummyExchange()
        result = ex.fetch("/test")
        assert result == {}
        ex.close()
