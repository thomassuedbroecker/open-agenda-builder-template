"""Tests for API endpoints."""

import json
from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app" in data
    assert "version" in data


def test_get_sessions_endpoint(client: TestClient):
    """Test getting sessions endpoint."""
    response = client.get("/api/sessions")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data


def test_add_session_to_agenda(client: TestClient):
    """Test adding a session to the browser-scoped agenda."""
    session_id = client.get("/api/sessions").json()[0]["id"]

    response = client.post(f"/api/agenda/add?session_id={session_id}")

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["conflicts"] == []

    agenda_sessions = client.get("/api/agenda/sessions").json()
    assert [item["id"] for item in agenda_sessions] == [session_id]


def test_agenda_isolation_by_cookie():
    """Test that separate browser sessions do not share one agenda."""
    with TestClient(app) as client_a, TestClient(app) as client_b:
        client_a.get("/health")
        client_b.get("/health")
        session_id = client_a.get("/api/sessions").json()[0]["id"]

        add_response = client_a.post(f"/api/agenda/add?session_id={session_id}")
        assert add_response.status_code == 200

        client_a_sessions = client_a.get("/api/agenda/sessions").json()
        client_b_sessions = client_b.get("/api/agenda/sessions").json()

        assert [item["id"] for item in client_a_sessions] == [session_id]
        assert client_b_sessions == []


def test_export_json_contains_generic_event_metadata(client: TestClient):
    """Test exporting agenda as JSON."""
    session_id = client.get("/api/sessions").json()[0]["id"]
    client.post(f"/api/agenda/add?session_id={session_id}")

    response = client.get("/api/agenda/export/json")

    assert response.status_code == 200
    data = response.json()
    assert data["event_name"]
    assert data["event_date"]
    assert data["session_ids"] == [session_id]


def test_export_ics_empty_agenda(client: TestClient):
    """Test exporting empty agenda as ICS."""
    response = client.get("/api/agenda/export/ics")

    assert response.status_code == 404


def test_export_ics_contains_calendar_data(client: TestClient):
    """Test exporting agenda as ICS."""
    session_id = client.get("/api/sessions").json()[0]["id"]
    client.post(f"/api/agenda/add?session_id={session_id}")

    response = client.get("/api/agenda/export/ics")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/calendar")
    body = response.text
    assert "BEGIN:VCALENDAR" in body
    assert "PRODID:-//Open Agenda Builder Template//EN" in body
    assert f"UID:{session_id}@agenda-builder.local" in body


def test_import_agenda_invalid_json(client: TestClient):
    """Test importing invalid JSON."""
    files = {"file": ("test.json", BytesIO(b"invalid json"), "application/json")}
    response = client.post("/api/agenda/import", files=files)

    assert response.status_code == 400
    data = response.json()
    assert "invalid json" in data["detail"].lower()


def test_import_agenda_missing_fields(client: TestClient):
    """Test importing JSON with missing fields."""
    invalid_data = {"wrong_field": "value"}
    files = {
        "file": (
            "test.json",
            BytesIO(json.dumps(invalid_data).encode()),
            "application/json",
        )
    }
    response = client.post("/api/agenda/import", files=files)

    assert response.status_code == 400
    data = response.json()
    assert "invalid json format" in data["detail"].lower()


def test_import_agenda_wrong_version(client: TestClient):
    """Test importing JSON with wrong version."""
    invalid_data = {"version": "2.0", "session_ids": []}
    files = {
        "file": (
            "test.json",
            BytesIO(json.dumps(invalid_data).encode()),
            "application/json",
        )
    }
    response = client.post("/api/agenda/import", files=files)

    assert response.status_code == 400
    data = response.json()
    assert "unsupported schema version" in data["detail"].lower()


def test_import_agenda_valid(client: TestClient):
    """Test importing a valid agenda export."""
    sessions = client.get("/api/sessions").json()
    selected_ids = [sessions[0]["id"], sessions[-1]["id"]]
    valid_data = {
        "version": "1.0",
        "session_ids": selected_ids,
    }
    files = {
        "file": (
            "agenda.json",
            BytesIO(json.dumps(valid_data).encode()),
            "application/json",
        )
    }

    response = client.post("/api/agenda/import", files=files)

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["session_count"] == 2

    agenda_sessions = client.get("/api/agenda/sessions").json()
    assert [item["id"] for item in agenda_sessions] == selected_ids


def test_clear_agenda(client: TestClient):
    """Test clearing agenda."""
    session_id = client.get("/api/sessions").json()[0]["id"]
    client.post(f"/api/agenda/add?session_id={session_id}")

    response = client.delete("/api/agenda/clear")

    assert response.status_code == 200
    assert client.get("/api/agenda/sessions").json() == []


def test_remove_session_not_found(client: TestClient):
    """Test removing non-existent session."""
    response = client.delete("/api/agenda/remove/non-existent")

    assert response.status_code == 404


def test_web_pages(client: TestClient):
    """Test both HTML pages load."""
    index_response = client.get("/")
    agenda_response = client.get("/my-agenda")

    assert index_response.status_code == 200
    assert "text/html" in index_response.headers["content-type"]
    assert agenda_response.status_code == 200
    assert "text/html" in agenda_response.headers["content-type"]
