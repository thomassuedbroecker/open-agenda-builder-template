# Test Section

This directory contains the Python test suite.

## Structure

- `conftest.py`: shared fixtures and service reset between tests
- `test_parser.py`: parser and schedule-loading tests
- `test_service.py`: agenda business-logic tests
- `test_api.py`: API and browser-isolation tests

## Execution

```bash
source .venv/bin/activate
python -m pytest
```

## Scope

The Python test suite verifies:

- Parser validation
- Track and time filtering
- Agenda overlap detection
- Import and export behavior
- Browser-scoped agenda isolation

Container smoke-test automation is documented separately in [deployment/README.md](../deployment/README.md) and implemented under [testing/](../testing).
