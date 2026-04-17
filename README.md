# dalal

Unified Python API for Indian stock exchanges (NSE + BSE).

## Install

```
pip install dalal
```

## Usage

```python
from dalal import Dalal

with Dalal() as d:
    d.quote("RELIANCE")                    # NSE (default)
    d.quote("500325", exchange="BSE")      # BSE
    d.fundamentals("500325")               # BSE-only
    d.actions("RELIANCE")                  # corporate actions
    d.history("RELIANCE", "2025-01-01", "2025-12-31")
```
