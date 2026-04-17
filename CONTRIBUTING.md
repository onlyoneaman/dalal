# Contributing to dalal

License: MIT (see LICENSE).

Thanks for contributing.

## Development setup
1. `python -m venv .venv`
2. `source .venv/bin/activate`
3. `pip install -e .[dev]`
4. `pytest -q`

## Branch and PR flow
1. Create a focused branch from `main`.
2. Make small, reviewable commits.
3. Add or update tests for behavioral changes.
4. Update docs and changelog when needed.
5. Open a PR using `.github/PULL_REQUEST_TEMPLATE.md`.

## Coding guidelines
- Python 3.11+.
- Keep runtime dependencies minimal.
- Keep APIs stable and additive where possible.
- Normalize output fields consistently across exchanges.

## Testing guidelines
- Use `responses` for HTTP mocking.
- Avoid live-network tests in normal CI.
- Include negative-path tests for new parsing/error branches.

## Release notes
Update `CHANGELOG.md` under `Unreleased` for non-trivial changes.

## Questions
Open a GitHub issue: https://github.com/onlyoneaman/dalal/issues
