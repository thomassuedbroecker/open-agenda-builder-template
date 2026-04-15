"""Pytest configuration and fixtures."""

from datetime import time
from typing import List

import pytest
from fastapi.testclient import TestClient

from app import dependencies
from app.main import app
from app.models.session import Session
from app.services.agenda_service import AgendaService


@pytest.fixture(autouse=True)
def reset_global_service() -> None:
    """Reset the shared service between tests."""
    dependencies._service = None
    yield
    dependencies._service = None


@pytest.fixture
def client() -> TestClient:
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def sample_sessions() -> List[Session]:
    """Create sample sessions for testing."""
    return [
        Session(
            id="session-1",
            name="Opening Remarks",
            start_time=time(10, 0),
            end_time=time(10, 30),
            stage="Main Stage",
            speaker="Program Team",
            format="Briefing",
            topic="Welcome",
            location="Hall A",
        ),
        Session(
            id="session-2",
            name="Operations Planning",
            start_time=time(10, 30),
            end_time=time(11, 30),
            stage="Workshop Room",
            speaker="Operations Lead",
            format="Workshop",
            topic="Planning",
            location="Room 1",
        ),
        Session(
            id="session-3",
            name="Platform Roundtable",
            start_time=time(11, 0),
            end_time=time(12, 0),
            stage="Main Stage",
            speaker="Panel Hosts",
            format="Panel",
            topic="Platform",
            location="Hall A",
        ),
        Session(
            id="session-4",
            name="Customer Workshop",
            start_time=time(14, 0),
            end_time=time(14, 30),
            stage="Main Stage",
            speaker="Customer Team",
            format="Workshop",
            topic="Experience",
            location="Hall B",
        ),
    ]


@pytest.fixture
def agenda_service(sample_sessions: List[Session]) -> AgendaService:
    """Create an agenda service with sample sessions."""
    service = AgendaService()
    service._sessions_by_id = {s.id: s for s in sample_sessions}
    return service
