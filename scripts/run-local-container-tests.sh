#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE_NAME="${IMAGE_NAME:-open-event-agenda-builder:local-test}"
CONTAINER_NAME="${CONTAINER_NAME:-open-event-agenda-builder-local-test}"
HOST_PORT="${HOST_PORT:-18082}"
BASE_URL="http://127.0.0.1:${HOST_PORT}"
STATUS_JSON="${ROOT_DIR}/testing/local-container-status.json"
STATUS_MARKDOWN="${ROOT_DIR}/docs/local-container-test-status.md"
README_PATH="${ROOT_DIR}/README.md"

write_failure_status() {
  local message="$1"
  python3 - "$STATUS_JSON" "$STATUS_MARKDOWN" "$README_PATH" "$BASE_URL" "$message" <<'PY'
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

status_json, status_markdown, readme_path, base_url, message = sys.argv[1:]
timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
payload = {
    "status": "FAIL",
    "executed_at_utc": timestamp,
    "base_url": base_url,
    "checks": [{"name": "container-startup", "status": "FAIL", "details": message}],
}
Path(status_json).parent.mkdir(parents=True, exist_ok=True)
Path(status_json).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
Path(status_markdown).parent.mkdir(parents=True, exist_ok=True)
Path(status_markdown).write_text(
    "\n".join(
        [
            "# Local Container Test Status",
            "",
            "- Status: `FAIL`",
            f"- Executed at (UTC): `{timestamp}`",
            f"- Base URL: `{base_url}`",
            "",
            "## Checks",
            "",
            f"- `container-startup`: `FAIL` - {message}",
            "",
        ]
    ),
    encoding="utf-8",
)
start = "<!-- local-container-status:start -->"
end = "<!-- local-container-status:end -->"
readme = Path(readme_path).read_text(encoding="utf-8")
block = "\n".join(
    [
        start,
        "- Latest local container test: `FAIL`",
        f"- Executed at (UTC): `{timestamp}`",
        "- Verification command: `bash scripts/run-local-container-tests.sh`",
        "- Detailed report: [docs/local-container-test-status.md](docs/local-container-test-status.md)",
        "- Check `container-startup`: `FAIL`",
        end,
    ]
)
if start in readme and end in readme:
    before, remainder = readme.split(start, maxsplit=1)
    _, after = remainder.split(end, maxsplit=1)
    readme = before + block + after
else:
    readme = block + "\n\n" + readme
Path(readme_path).write_text(readme, encoding="utf-8")
PY
}

cleanup() {
  docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
}

trap cleanup EXIT

cleanup

if ! docker build -t "${IMAGE_NAME}" "${ROOT_DIR}"; then
  write_failure_status "docker build failed"
  exit 1
fi

if ! docker run -d --rm --name "${CONTAINER_NAME}" -p "${HOST_PORT}:8082" "${IMAGE_NAME}" >/dev/null; then
  write_failure_status "docker run failed"
  exit 1
fi

healthy=0
for _ in $(seq 1 30); do
  if curl -fsS "${BASE_URL}/health" >/dev/null; then
    healthy=1
    break
  fi
  sleep 2
done

if [ "${healthy}" -ne 1 ]; then
  write_failure_status "container did not become healthy within 60 seconds"
  exit 1
fi

python3 "${ROOT_DIR}/testing/local_container_smoke_test.py" \
  --base-url "${BASE_URL}" \
  --status-json "${STATUS_JSON}" \
  --status-markdown "${STATUS_MARKDOWN}" \
  --readme "${README_PATH}"
