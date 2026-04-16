# Dependency And Tooling Transparency

Navigation: [Repository Root](../README.md) | [Docs Index](README.md) | [Examples](../examples/README.md)

This document records the open-source runtime, library, and verification tooling used by Open Agenda Builder Template.

## Table of Contents

1. [Project License](#1-project-license)
2. [Transparency Principles](#2-transparency-principles)
3. [Production Dependencies](#3-production-dependencies)
4. [Development And Verification Dependencies](#4-development-and-verification-dependencies)
5. [Open-Source Tooling Outside Python](#5-open-source-tooling-outside-python)
6. [Removed Dependencies](#6-removed-dependencies)
7. [Compatibility Summary](#7-compatibility-summary)
8. [Supply-Chain Maintenance](#8-supply-chain-maintenance)

## 1. Project License

- Project license: Apache License 2.0
- Source files: [LICENSE](../LICENSE)
- Notice file: [NOTICE](../NOTICE)

## 2. Transparency Principles

1. Open-source components only
2. Pinned Python dependencies
3. No proprietary cloud runtime requirement
4. No mandatory third-party SaaS integration
5. Deterministic local-container verification

## 3. Production Dependencies

### 3.1 FastAPI 0.115.0

- License: MIT
- Purpose: Web framework for API and HTML endpoints

### 3.2 Uvicorn 0.32.0

- License: BSD-3-Clause
- Purpose: ASGI server

### 3.3 Jinja2 3.1.4

- License: BSD-3-Clause
- Purpose: Server-side HTML templates

### 3.4 Pydantic 2.9.2

- License: MIT
- Purpose: Data validation and serialization

### 3.5 Pydantic-Settings 2.5.2

- License: MIT
- Purpose: Typed environment configuration

### 3.6 iCalendar 6.0.1

- License: BSD-2-Clause
- Purpose: ICS export generation

### 3.7 python-multipart 0.0.12

- License: Apache-2.0
- Purpose: JSON import upload handling

## 4. Development And Verification Dependencies

### 4.1 pytest 8.3.3

- License: MIT
- Purpose: Automated Python test execution

### 4.2 pytest-asyncio 0.24.0

- License: Apache-2.0
- Purpose: Async test support

### 4.3 pytest-cov 5.0.0

- License: MIT
- Purpose: Coverage reporting

### 4.4 httpx 0.27.2

- License: BSD-3-Clause
- Purpose: Test transport used indirectly by FastAPI and Starlette test clients

### 4.5 Ruff 0.7.0

- License: MIT
- Purpose: Linting

### 4.6 mypy 1.13.0

- License: MIT
- Purpose: Static type checking

### 4.7 IPython 8.29.0

- License: BSD-3-Clause
- Purpose: Optional interactive development shell

## 5. Open-Source Tooling Outside Python

### 5.1 Python 3.12

- License: PSF License
- Purpose: Declared runtime and local test interpreter

### 5.2 Docker

- License model varies by edition and distribution, but the project relies on the open container standard and local Docker-compatible engines for build and runtime testing.
- Purpose: Single-container runtime and smoke-test target

### 5.3 Bash

- License: GPL-compatible GNU Bash distribution on most systems
- Purpose: Local automation scripts

### 5.4 curl

- License: curl license
- Purpose: Health-check and smoke-test orchestration

## 6. Removed Dependencies

The current runtime application no longer depends on:

- `beautifulsoup4`

`httpx` remains in the development toolchain because the FastAPI and Starlette test client requires it. `beautifulsoup4` was removed because the application no longer scrapes live third-party websites.

## 7. Compatibility Summary

All bundled Python dependencies use permissive open-source licenses that are compatible with Apache License 2.0 for this project.

## 8. Supply-Chain Maintenance

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
