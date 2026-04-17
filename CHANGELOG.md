# Changelog

License: MIT (see LICENSE).

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic Versioning.

## [Unreleased]

## [0.1.3] - 2026-04-17
### Added
- `llms.txt` and `llms-full.txt` for LLM/agent context.
- `AGENTS.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, and `DISCLAIMER.md`.
- `.github/PULL_REQUEST_TEMPLATE.md`.
- `dalal/py.typed` and packaging metadata for typed consumers.

### Changed
- Enriched `pyproject.toml` metadata: classifiers, keywords, repository URLs.

## [0.1.2] - 2026-04-17
### Added
- Unified NSE + BSE API surface for quotes, actions, status, lookup, and more.
- NSE historical OHLCV access and market breadth helpers.
- BSE fundamentals/meta/result calendar helpers.
- Built-in rate limiting and typed exception hierarchy.
