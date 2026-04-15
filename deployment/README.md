# Deployment Section

This section documents the supported runtime path for the repository.

## Supported Mode

- Local single-container deployment with Docker

## Key Files

- [docs/DEPLOYMENT.md](../docs/DEPLOYMENT.md): deployment runbook
- [scripts/deploy.sh](../scripts/deploy.sh): local container start helper
- [scripts/run-local-container-tests.sh](../scripts/run-local-container-tests.sh): authoritative deployment verification command
- [docs/local-container-test-status.md](../docs/local-container-test-status.md): latest human-readable execution status

## Why This Exists

Deployment behavior must stay synchronized with:

1. The container image in [Dockerfile](../Dockerfile)
2. The smoke test automation
3. The README status block

This section also supports the twelve-factor split between build, release, and run by keeping deployment instructions separate from application code.
