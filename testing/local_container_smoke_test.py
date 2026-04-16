"""Local-container smoke test for the Open Agenda Builder Template."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from http.cookiejar import CookieJar
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import HTTPCookieProcessor, Request, build_opener


README_STATUS_START = "<!-- local-container-status:start -->"
README_STATUS_END = "<!-- local-container-status:end -->"


@dataclass
class CheckResult:
    """Represents one smoke-test check."""

    name: str
    status: str
    details: str


def build_opener_with_cookies():
    """Create an opener that preserves cookies between requests."""
    return build_opener(HTTPCookieProcessor(CookieJar()))


def request_json(opener, method: str, url: str, data: bytes | None = None) -> Any:
    """Send a request and decode a JSON response."""
    request = Request(url, data=data, method=method)
    with opener.open(request, timeout=10) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def request_text(opener, method: str, url: str) -> str:
    """Send a request and decode a text response."""
    request = Request(url, method=method)
    with opener.open(request, timeout=10) as response:
        return response.read().decode("utf-8")


def render_status_block(status: str, timestamp: str, checks: list[CheckResult]) -> str:
    """Render the README status block."""
    def get_icon(s: str) -> str:
        if s == "PASS":
            return "✅"
        elif s == "FAIL":
            return "❌"
        else:
            return "⚠️"
    
    lines = [
        README_STATUS_START,
        f"- Latest local container test: {get_icon(status)} `{status}`",
        f"- Executed at (UTC): `{timestamp}`",
        f"- Verification command: `bash scripts/run-local-container-tests.sh`",
        f"- Detailed report: [docs/local-container-test-status.md](docs/local-container-test-status.md)",
    ]
    for check in checks:
        lines.append(f"- Check `{check.name}`: {get_icon(check.status)} `{check.status}`")
    lines.append(README_STATUS_END)
    return "\n".join(lines)


def write_status_files(
    *,
    status: str,
    base_url: str,
    checks: list[CheckResult],
    status_json_path: Path,
    status_markdown_path: Path,
    readme_path: Path,
) -> None:
    """Write JSON, markdown, and README status outputs."""
    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    payload = {
        "status": status,
        "executed_at_utc": timestamp,
        "base_url": base_url,
        "checks": [asdict(check) for check in checks],
    }
    status_json_path.parent.mkdir(parents=True, exist_ok=True)
    status_json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    md_lines = [
        "# Local Container Test Status",
        "",
        f"- Status: `{status}`",
        f"- Executed at (UTC): `{timestamp}`",
        f"- Base URL: `{base_url}`",
        "",
        "## Checks",
        "",
    ]
    for check in checks:
        md_lines.append(f"- `{check.name}`: `{check.status}` - {check.details}")
    status_markdown_path.parent.mkdir(parents=True, exist_ok=True)
    status_markdown_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    readme_content = readme_path.read_text(encoding="utf-8")
    status_block = render_status_block(status, timestamp, checks)
    if README_STATUS_START in readme_content and README_STATUS_END in readme_content:
        before, remainder = readme_content.split(README_STATUS_START, maxsplit=1)
        _, after = remainder.split(README_STATUS_END, maxsplit=1)
        readme_content = before + status_block + after
    else:
        readme_content = status_block + "\n\n" + readme_content
    readme_path.write_text(readme_content, encoding="utf-8")


def run_smoke_test(base_url: str) -> list[CheckResult]:
    """Run end-to-end smoke tests against the containerized application."""
    checks: list[CheckResult] = []
    primary_client = build_opener_with_cookies()
    secondary_client = build_opener_with_cookies()

    health = request_json(primary_client, "GET", f"{base_url}/health")
    if health.get("status") != "healthy":
        raise AssertionError("Health endpoint did not report healthy status")
    checks.append(CheckResult("health", "PASS", "Health endpoint responded with healthy status"))

    sessions = request_json(primary_client, "GET", f"{base_url}/api/sessions")
    if not isinstance(sessions, list) or not sessions:
        raise AssertionError("No sessions available in the schedule")
    checks.append(CheckResult("sessions", "PASS", f"Loaded {len(sessions)} sessions from the container"))

    session_id = str(sessions[0]["id"])
    add_result = request_json(
        primary_client,
        "POST",
        f"{base_url}/api/agenda/add?session_id={quote(session_id)}",
    )
    if add_result.get("success") is not True:
        raise AssertionError("Failed to add a session to the agenda")
    checks.append(CheckResult("agenda-add", "PASS", f"Added session `{session_id}`"))

    agenda_sessions = request_json(primary_client, "GET", f"{base_url}/api/agenda/sessions")
    if [session["id"] for session in agenda_sessions] != [session_id]:
        raise AssertionError("Agenda did not contain the expected session")
    checks.append(CheckResult("agenda-read", "PASS", "Primary browser session retained its agenda"))

    request_json(secondary_client, "GET", f"{base_url}/health")
    secondary_agenda = request_json(secondary_client, "GET", f"{base_url}/api/agenda/sessions")
    if secondary_agenda:
        raise AssertionError("Secondary browser session should not share the first user's agenda")
    checks.append(CheckResult("session-isolation", "PASS", "Separate browser cookies receive separate agendas"))

    export_json = request_json(primary_client, "GET", f"{base_url}/api/agenda/export/json")
    if not export_json.get("event_name") or export_json.get("session_ids") != [session_id]:
        raise AssertionError("Export JSON did not include the expected event metadata")
    checks.append(CheckResult("export-json", "PASS", "JSON export contains generic event metadata"))

    agenda_page = request_text(primary_client, "GET", f"{base_url}/my-agenda")
    if "AI Conference" in agenda_page:
        raise AssertionError("Legacy hardcoded conference branding is still present in the agenda page")
    checks.append(CheckResult("branding", "PASS", "Agenda page is free of legacy hardcoded event branding"))

    return checks


def main() -> int:
    """Run the smoke test and persist the result."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--status-json", required=True)
    parser.add_argument("--status-markdown", required=True)
    parser.add_argument("--readme", required=True)
    args = parser.parse_args()

    status_json_path = Path(args.status_json)
    status_markdown_path = Path(args.status_markdown)
    readme_path = Path(args.readme)

    try:
        checks = run_smoke_test(args.base_url)
        status = "PASS"
    except (AssertionError, HTTPError, URLError, json.JSONDecodeError) as exc:
        checks = [CheckResult("smoke-test", "FAIL", str(exc))]
        status = "FAIL"
    except Exception as exc:  # pragma: no cover - defensive catch for shell integration
        checks = [CheckResult("smoke-test", "FAIL", f"Unexpected error: {exc}")]
        status = "FAIL"

    write_status_files(
        status=status,
        base_url=args.base_url,
        checks=checks,
        status_json_path=status_json_path,
        status_markdown_path=status_markdown_path,
        readme_path=readme_path,
    )
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
