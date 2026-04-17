# AGENTS.md

License: MIT (see LICENSE).

This file defines practical rules for AI and human contributors working in this repository.

## Goal
Maintain a stable, low-dependency Python API for NSE/BSE market data.

## Fast start
- Create env: `python -m venv .venv && source .venv/bin/activate`
- Install: `pip install -e .[dev]`
- Run tests: `pytest -q`

## Source map
- `dalal/dalal.py`: entrypoint router and exchange dispatch
- `dalal/nse.py`: NSE implementation
- `dalal/bse.py`: BSE implementation
- `dalal/base.py`: shared HTTP/rate-limit behavior
- `dalal/errors.py`: exception hierarchy
- `tests/`: API behavior and parsing tests

## Contribution rules
- Keep public API backward compatible unless intentionally doing a major-version break.
- Preserve lazy session semantics (`Dalal` should not initialize exchange sessions until needed).
- Do not remove default rate limiting.
- Keep runtime deps minimal; avoid new deps unless clearly justified.
- Add tests for every bugfix or new endpoint parser.

## Testing rules
- Tests must be deterministic and offline.
- Use mocked HTTP via `responses`; do not hit live NSE/BSE in CI tests.
- Prefer asserting stable output keys and numeric/date normalization.

## Error handling rules
- Raise existing typed exceptions where possible (`ValidationError`, `SymbolNotFound`, etc.).
- Keep exception inheritance consistent with `dalal/errors.py`.

## Docs rules
- Update `README.md` for user-visible API changes.
- Update `llms.txt` and `llms-full.txt` when adding/removing public methods.
- Update `CHANGELOG.md` for behavior changes.

## Out of scope
- Portfolio advice, trading recommendations, or strategy guidance.
- Any claim of official endorsement by NSE/BSE.
