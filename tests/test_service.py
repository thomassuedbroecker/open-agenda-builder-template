"""Tests for the agenda service."""

from typing import List

import pytest

from app.models.personal_agenda import PersonalAgenda
from app.models.session import Session
from app.services.agenda_service import AgendaService


def test_create_personal_agenda(agenda_service: AgendaService):
    """Test creating a personal agenda."""
    agenda = agenda_service.create_personal_agenda()
    
    assert agenda is not None
    assert agenda.sessions == []
    assert agenda.version == "1.0"


def test_get_all_sessions(agenda_service: AgendaService, sample_sessions: List[Session]):
    """Test getting all sessions."""
    sessions = agenda_service.get_all_sessions()
    
    assert len(sessions) == len(sample_sessions)
    assert all(isinstance(s, Session) for s in sessions)


def test_get_session_by_id(agenda_service: AgendaService):
    """Test getting a session by ID."""
    session = agenda_service.get_session_by_id("session-1")
    
    assert session is not None
    assert session.id == "session-1"
    assert session.name == "Opening Remarks"


def test_get_session_by_id_not_found(agenda_service: AgendaService):
    """Test getting a non-existent session."""
    session = agenda_service.get_session_by_id("non-existent")
    
    assert session is None


@pytest.mark.asyncio
async def test_add_session_to_agenda(agenda_service: AgendaService):
    """Test adding a session to agenda."""
    agenda = PersonalAgenda()
    success, error = await agenda_service.add_session_to_agenda(agenda, "session-1")
    
    assert success is True
    assert error is None
    
    assert "session-1" in agenda.sessions


@pytest.mark.asyncio
async def test_add_session_already_added(agenda_service: AgendaService):
    """Test adding a session that's already in the agenda."""
    agenda = PersonalAgenda()
    await agenda_service.add_session_to_agenda(agenda, "session-1")
    success, error = await agenda_service.add_session_to_agenda(agenda, "session-1")
    
    assert success is False
    assert "already in agenda" in error.lower()


@pytest.mark.asyncio
async def test_add_session_not_found(agenda_service: AgendaService):
    """Test adding a non-existent session."""
    success, error = await agenda_service.add_session_to_agenda(PersonalAgenda(), "non-existent")
    
    assert success is False
    assert "not found" in error.lower()


@pytest.mark.asyncio
async def test_add_overlapping_sessions(agenda_service: AgendaService):
    """Test adding overlapping sessions."""
    agenda = PersonalAgenda()
    await agenda_service.add_session_to_agenda(agenda, "session-2")
    
    success, error = await agenda_service.add_session_to_agenda(agenda, "session-3")
    
    assert success is False
    assert "overlaps" in error.lower()


@pytest.mark.asyncio
async def test_add_non_overlapping_sessions(agenda_service: AgendaService):
    """Test adding non-overlapping sessions."""
    agenda = PersonalAgenda()
    success1, _ = await agenda_service.add_session_to_agenda(agenda, "session-1")
    
    success2, _ = await agenda_service.add_session_to_agenda(agenda, "session-2")
    
    assert success1 is True
    assert success2 is True
    
    assert len(agenda.sessions) == 2


@pytest.mark.asyncio
async def test_remove_session_from_agenda(agenda_service: AgendaService):
    """Test removing a session from agenda."""
    agenda = PersonalAgenda()
    await agenda_service.add_session_to_agenda(agenda, "session-1")
    
    success = agenda_service.remove_session_from_agenda(agenda, "session-1")
    
    assert success is True
    
    assert "session-1" not in agenda.sessions


def test_remove_session_not_in_agenda(agenda_service: AgendaService):
    """Test removing a session that's not in the agenda."""
    success = agenda_service.remove_session_from_agenda(PersonalAgenda(), "session-1")
    
    assert success is False


@pytest.mark.asyncio
async def test_get_agenda_sessions(agenda_service: AgendaService):
    """Test getting all sessions in an agenda."""
    agenda = PersonalAgenda()
    await agenda_service.add_session_to_agenda(agenda, "session-1")
    await agenda_service.add_session_to_agenda(agenda, "session-4")
    
    sessions = agenda_service.get_agenda_sessions(agenda)
    
    assert len(sessions) == 2
    assert sessions[0].id == "session-1"
    assert sessions[1].id == "session-4"


def test_get_agenda_sessions_empty(agenda_service: AgendaService):
    """Test getting sessions from an empty agenda."""
    sessions = agenda_service.get_agenda_sessions(PersonalAgenda())
    
    assert sessions == []


def test_get_conflicts_for_session_excludes_selected_session(agenda_service: AgendaService):
    """Test conflict lookup excludes the selected session itself."""
    agenda = PersonalAgenda(sessions=["session-2", "session-3"])

    conflicts = agenda_service.get_conflicts_for_session(agenda, "session-2")

    assert [session.id for session in conflicts] == ["session-3"]


@pytest.mark.asyncio
async def test_import_agenda_valid(agenda_service: AgendaService):
    """Test importing a valid agenda."""
    session_ids = ["session-1", "session-4"]
    
    success, error = await agenda_service.import_agenda(session_ids)
    
    assert success is True
    assert error is None
    
@pytest.mark.asyncio
async def test_import_agenda_invalid_ids(agenda_service: AgendaService):
    """Test importing agenda with invalid session IDs."""
    session_ids = ["session-1", "non-existent"]
    
    success, error = await agenda_service.import_agenda(session_ids)
    
    assert success is False
    assert "invalid session ids" in error.lower()


@pytest.mark.asyncio
async def test_import_agenda_with_overlaps(agenda_service: AgendaService):
    """Test importing agenda with overlapping sessions."""
    session_ids = ["session-2", "session-3"]
    
    success, error = await agenda_service.import_agenda(session_ids)
    
    assert success is False
    assert "overlaps" in error.lower()


@pytest.mark.asyncio
async def test_clear_agenda(agenda_service: AgendaService):
    """Test clearing an agenda."""
    agenda = PersonalAgenda()
    await agenda_service.add_session_to_agenda(agenda, "session-1")
    await agenda_service.add_session_to_agenda(agenda, "session-4")
    
    success = agenda_service.clear_agenda(agenda)
    
    assert success is True
    
    assert len(agenda.sessions) == 0


def test_clear_agenda_not_found(agenda_service: AgendaService):
    """Test clearing an empty agenda still succeeds."""
    success = agenda_service.clear_agenda(PersonalAgenda())
    
    assert success is True


def test_session_overlap_detection():
    """Test session overlap detection."""
    from datetime import time
    
    session1 = Session(
        id="s1",
        name="Session 1",
        start_time=time(10, 0),
        end_time=time(11, 0),
        stage="Stage",
        speaker="Speaker",
        format="Talk",
        topic="Topic",
    )
    
    session2 = Session(
        id="s2",
        name="Session 2",
        start_time=time(10, 30),
        end_time=time(11, 30),
        stage="Stage",
        speaker="Speaker",
        format="Talk",
        topic="Topic",
    )
    
    session3 = Session(
        id="s3",
        name="Session 3",
        start_time=time(11, 0),
        end_time=time(12, 0),
        stage="Stage",
        speaker="Speaker",
        format="Talk",
        topic="Topic",
    )
    
    assert session1.overlaps_with(session2) is True
    assert session2.overlaps_with(session1) is True
    
    assert session1.overlaps_with(session3) is False
    assert session3.overlaps_with(session1) is False
