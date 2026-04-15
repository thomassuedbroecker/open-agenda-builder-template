# Deployment Guide

## Supported Deployment Mode

The repository currently documents and verifies one deployment mode only:

- Local single-container runtime with Docker

This is deliberate. The test automation is aligned to this mode, and the README status block is generated from that exact execution path.

## Prerequisites

- Docker
- Bash
- curl
- Python 3 for the local smoke-test helper script

## Build The Container

```bash
docker build -t open-event-agenda-builder .
```

## Run The Container

```bash
docker run --rm -p 8082:8082 open-event-agenda-builder
```

Then open:

- App: `http://localhost:8082`
- Health: `http://localhost:8082/health`

## Verified Local Deployment Script

For the repository-supported verification path, use:

```bash
bash scripts/run-local-container-tests.sh
```

This script:

1. Builds the image locally
2. Starts the container
3. Waits for health status
4. Runs the HTTP smoke test
5. Writes status artifacts used by the documentation

## Environment Variables

The container supports generic event configuration through environment variables, for example:

```bash
docker run --rm -p 8082:8082 \
  -e EVENT_NAME="Internal Planning Day" \
  -e EVENT_DATE="2026-09-24" \
  -e EVENT_DAY_LABEL="Day 1" \
  -e TRACK_FILTER="Operations" \
  -e SECURE_COOKIE=false \
  open-event-agenda-builder
```

For the full variable set, see [.env.example](../.env.example).

## Operational Notes

- The application keeps user agenda state in one essential browser-session cookie
- The application process stays stateless with respect to user-specific agenda data
- Concurrent users are isolated by separate browser cookies
- For HTTPS deployments, set `SECURE_COOKIE=true`

## Troubleshooting

### Container Does Not Start

- Check Docker is running
- Rebuild the image without cache if needed:

```bash
docker build --no-cache -t open-event-agenda-builder .
```

### Health Check Fails

- Inspect container logs:

```bash
docker logs <container-name>
```

- Verify port `8082` is not already in use

### Smoke Test Fails

- Read [docs/local-container-test-status.md](local-container-test-status.md)
- Inspect [testing/local-container-status.json](../testing/local-container-status.json)
- Re-run `bash scripts/run-local-container-tests.sh`
