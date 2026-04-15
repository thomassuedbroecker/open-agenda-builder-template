# Dependency And Tooling Transparency

This document records the open-source runtime, library, and verification tooling used by Open Event Agenda Builder.

## Project License

- Project license: Apache License 2.0
- Source files: [LICENSE](LICENSE)
- Notice file: [NOTICE](NOTICE)

## Transparency Principles

1. Open-source components only
2. Pinned Python dependencies
3. No proprietary cloud runtime requirement
4. No mandatory third-party SaaS integration
5. Deterministic local-container verification

## Production Dependencies

### FastAPI 0.115.0

- License: MIT
- Purpose: Web framework for API and HTML endpoints

### Uvicorn 0.32.0

- License: BSD-3-Clause
- Purpose: ASGI server

### Jinja2 3.1.4

- License: BSD-3-Clause
- Purpose: Server-side HTML templates

### Pydantic 2.9.2

- License: MIT
- Purpose: Data validation and serialization

### Pydantic-Settings 2.5.2

- License: MIT
- Purpose: Typed environment configuration

### iCalendar 6.0.1

- License: BSD-2-Clause
- Purpose: ICS export generation

### python-multipart 0.0.12

- License: Apache-2.0
- Purpose: JSON import upload handling

## Development And Verification Dependencies

### pytest 8.3.3

- License: MIT
- Purpose: Automated Python test execution

### pytest-asyncio 0.24.0

- License: Apache-2.0
- Purpose: Async test support

### pytest-cov 5.0.0

- License: MIT
- Purpose: Coverage reporting

### httpx 0.27.2

- License: BSD-3-Clause
- Purpose: Test transport used indirectly by FastAPI and Starlette test clients

### Ruff 0.7.0

- License: MIT
- Purpose: Linting

### mypy 1.13.0

- License: MIT
- Purpose: Static type checking

### IPython 8.29.0

- License: BSD-3-Clause
- Purpose: Optional interactive development shell

## Open-Source Tooling Outside Python

### Python 3.12

- License: PSF License
- Purpose: Declared runtime and local test interpreter

### Docker

- License model varies by edition and distribution, but the project relies on the open container standard and local Docker-compatible engines for build and runtime testing.
- Purpose: Single-container runtime and smoke-test target

### Bash

- License: GPL-compatible GNU Bash distribution on most systems
- Purpose: Local automation scripts

### curl

- License: curl license
- Purpose: Health-check and smoke-test orchestration

## Removed Dependencies

The current runtime application no longer depends on:

- `beautifulsoup4`

`httpx` remains in the development toolchain because the FastAPI and Starlette test client requires it. `beautifulsoup4` was removed because the application no longer scrapes live third-party websites.

## Compatibility Summary

All bundled Python dependencies use permissive open-source licenses that are compatible with Apache License 2.0 for this project.

## Supply-Chain Maintenance

Recommended maintenance workflow:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest
bash scripts/run-local-container-tests.sh
```

When dependencies change, update:

1. `requirements.txt`
2. `requirements-dev.txt`
3. `pyproject.toml`
4. This document
5. The executed test status artifacts if behavior changed
