# dalal

[![PyPI version](https://img.shields.io/pypi/v/dalal.svg)](https://pypi.org/project/dalal/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://github.com/onlyoneaman/dalal/actions/workflows/tests.yml/badge.svg)](https://github.com/onlyoneaman/dalal/actions)

Unified Python API for Indian stock exchanges (NSE + BSE). One class, both exchanges.

No API keys. No third-party exchange wrappers. Just `requests` under the hood.

## Install

```bash
pip install dalal
```

## Quick Start

```python
from dalal import Dalal

with Dalal() as d:
    # NSE (default)
    d.quote("RELIANCE")
    d.history("RELIANCE", "2025-01-01", "2025-12-31")
    d.actions("RELIANCE")

    # BSE
    d.quote("500325", exchange="BSE")
    d.fundamentals("500325")
    d.meta("500325")
```

## Features

| Method | NSE | BSE | Default | Description |
|---|---|---|---|---|
| `quote()` | Yes | Yes | NSE | Live price, OHLC, 52-week range |
| `history()` | Yes | - | NSE | Historical OHLCV (auto-chunks 100-day windows) |
| `actions()` | Yes | Yes | NSE | Corporate actions — dividends, splits, bonuses |
| `fundamentals()` | - | Yes | BSE | 3-period results — Revenue, PAT, EPS, OPM%, NPM% |
| `meta()` | - | Yes | BSE | PE, ROE, EPS, P/B ratios |
| `index()` | Yes | - | NSE | Index constituents with live prices |
| `holidays()` | Yes | - | NSE | Trading/clearing holidays |
| `bulk_deals()` | Yes | - | NSE | Historical bulk deal data |
| `block_deals()` | Yes | - | NSE | Intraday block deals |
| `shareholding()` | Yes | - | NSE | Promoter/public/FII holding pattern |
| `gainers()` | Yes | Yes | NSE | Top gainers by index |
| `losers()` | Yes | Yes | NSE | Top losers by index |
| `announcements()` | Yes | Yes | NSE | Corporate announcements |
| `status()` | Yes | Yes | NSE | Market open/closed status |
| `lookup()` | Yes | Yes | NSE | Symbol search / autocomplete |
| `result_calendar()` | - | Yes | BSE | Upcoming earnings dates |
| `advances()` | Yes | - | NSE | Advance/decline ratio |

## Usage

### Quotes

```python
with Dalal() as d:
    nse = d.quote("RELIANCE")
    # {'symbol': 'RELIANCE', 'ltp': 1365.1, 'open': 1360.0, 'high': 1370.0,
    #  'low': 1340.0, 'prev_close': 1350.0, 'year_high': 1600.0, ...}

    bse = d.quote("500325", exchange="BSE")
    # {'scripcode': '500325', 'ltp': 1365.1, 'open': 1340.0, ...}
```

### Historical Data

```python
with Dalal() as d:
    data = d.history("RELIANCE", "2025-01-01", "2025-06-30")
    # [{'date': '2025-01-02', 'open': 1300.0, 'high': 1320.0,
    #   'low': 1290.0, 'close': 1310.0, 'volume': 5000000.0}, ...]

    # Works with pandas
    import pandas as pd
    df = pd.DataFrame(data)
```

### Fundamentals (BSE)

```python
with Dalal() as d:
    f = d.fundamentals("500325")
    # {'scripcode': '500325', 'currency_unit': 'in Cr.',
    #  'periods': [
    #    {'period': 'Dec-25', 'revenue': 125741.0, 'net_profit': 9396.0,
    #     'eps': 6.94, 'opm_pct': 14.56, 'npm_pct': 7.47},
    #    {'period': 'Sep-25', ...},
    #    {'period': 'FY24-25', ...}
    #  ]}

    m = d.meta("500325")
    # {'eps': 35.21, 'pe': 38.77, 'roe': 9.09, 'pb': 3.52, ...}
```

### Corporate Actions

```python
with Dalal() as d:
    actions = d.actions("RELIANCE")
    # [{'symbol': 'RELIANCE', 'subject': 'Dividend - Rs 5.5 Per Share',
    #   'ex_date': '2025-08-14', ...},
    #  {'symbol': 'RELIANCE', 'subject': 'Bonus 1:1',
    #   'ex_date': '2024-10-28', ...}]
```

### Index Constituents

```python
with Dalal() as d:
    nifty = d.index("NIFTY 50")
    # {'name': 'NIFTY 50', 'advance': 30, 'decline': 20,
    #  'constituents': [
    #    {'symbol': 'RELIANCE', 'ltp': 1365.0, 'pct_change': 1.12, ...},
    #    ...
    #  ]}
```

## Error Handling

```python
from dalal import Dalal, SymbolNotFound, RateLimited, NetworkError

with Dalal() as d:
    try:
        d.quote("INVALID")
    except SymbolNotFound:
        print("Symbol not found")
    except RateLimited:
        print("Too many requests — slow down")
    except NetworkError:
        print("Connection issue")
```

All exceptions inherit from `DalalError`:

```
DalalError
├── ExchangeError
│   ├── AuthError
│   ├── SymbolNotFound
│   └── DataNotAvailable
├── NetworkError
│   ├── RateLimited
│   └── ExchangeDown
└── ValidationError
```

## Rate Limiting

Built-in rate limiting prevents IP bans:
- NSE: 3 requests/second
- BSE: 8 requests/second

Override if needed:
```python
d = Dalal(nse_rate=2, bse_rate=5)
```

## How It Works

`dalal` talks directly to the same APIs that nseindia.com and bseindia.com use internally. No API keys needed — it handles browser impersonation and cookie management automatically.

- **NSE**: Cookie-primed session (auto-refreshes on 401)
- **BSE**: Simple session with browser-like headers
- **Sessions are lazy**: NSE session only created on first NSE call, same for BSE

## Requirements

- Python 3.11+
- `requests >= 2.31`

## License

MIT

## Author

[Aman](https://amankumar.ai) ([@onlyoneaman](https://x.com/onlyoneaman))
