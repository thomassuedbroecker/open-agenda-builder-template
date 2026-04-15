#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE_NAME="${IMAGE_NAME:-open-event-agenda-builder}"
CONTAINER_NAME="${CONTAINER_NAME:-open-event-agenda-builder}"
HOST_PORT="${HOST_PORT:-8082}"

echo "Building local container image: ${IMAGE_NAME}"
docker build -t "${IMAGE_NAME}" "${ROOT_DIR}"

echo "Stopping existing container if present: ${CONTAINER_NAME}"
docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true

echo "Starting local container on http://127.0.0.1:${HOST_PORT}"
docker run -d --rm \
  --name "${CONTAINER_NAME}" \
  -p "${HOST_PORT}:8082" \
  "${IMAGE_NAME}" >/dev/null

echo "Container started."
echo "Application URL: http://127.0.0.1:${HOST_PORT}"
echo "Health URL: http://127.0.0.1:${HOST_PORT}/health"
