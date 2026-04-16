# Python Tests

Navigation: [Repository Root](../README.md) | [Testing Automation](../testing/README.md) | [Deployment](../deployment/README.md)

This directory contains the Python test suite.

## Table of Contents

1. [Purpose](#1-purpose)
2. [Structure](#2-structure)
3. [Execution](#3-execution)
4. [Scope](#4-scope)

## 1. Purpose

The tests in this directory verify the parser, service layer, API routes, and browser-scoped agenda behavior without requiring Docker.

## 2. Structure

- `conftest.py`: shared fixtures and service reset between tests
- `test_parser.py`: parser and schedule-loading tests
- `test_service.py`: agenda business-logic tests
- `test_api.py`: API, export/import, and browser-isolation tests

## 3. Execution

```bash
source .venv/bin/activate
python -m pytest

# or without shell activation
./.venv/bin/python -m pytest
```

## 4. Scope

The Python test suite verifies:

- Parser validation
- Track and time filtering
- Agenda overlap detection
- Agenda add, remove, clear, import, and export behavior
- Browser-scoped agenda isolation

Container smoke-test automation is documented separately in [deployment/README.md](../deployment/README.md) and implemented under [testing/](../testing/README.md).
