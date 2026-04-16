# Container Test Automation

Navigation: [Repository Root](../README.md) | [Deployment](../deployment/README.md) | [Latest Smoke-Test Status](../docs/local-container-test-status.md)

This directory contains the local-container smoke test implementation and generated status artifacts.

## Table of Contents

1. [Purpose](#1-purpose)
2. [Files](#2-files)
3. [Execution](#3-execution)
4. [Relationship To Tests](#4-relationship-to-tests)

## 1. Purpose

This directory covers the repository's deployment-path verification: build the image, run the container, hit the live HTTP endpoints, and persist the latest status artifacts used by the docs.

## 2. Files

- [local_container_smoke_test.py](local_container_smoke_test.py): HTTP smoke-test logic
- [local-container-status.json](local-container-status.json): latest machine-readable execution result

## 3. Execution

```bash
bash scripts/run-local-container-tests.sh
```

## 4. Relationship To Tests

- `tests/` contains Python unit and API tests
- `testing/` contains deployment-path smoke-test automation and generated output
