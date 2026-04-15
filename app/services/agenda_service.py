"""Business logic for managing personal agendas."""

import logging
from threading import RLock
from typing import Dict, List, Optional

from app.models.personal_agenda import PersonalAgenda
from app.models.session import Session
from app.services.agenda_parser import AgendaParser

logger = logging.getLogger(__name__)


class AgendaService:
    """Service for managing personal agendas."""

    def __init__(self) -> None:
        """Initialize the service."""
        self.parser = AgendaParser()
        self._sessions_by_id: Dict[str, Session] = {}
        self._lock = RLock()

    async def load_sessions(self) -> List[Session]:
        """Load and cache all available sessions."""
        # Check cache first
        cached = self.parser.get_cached_sessions()
        if cached:
            logger.info("Using cached sessions")
            with self._lock:
                self._sessions_by_id = {s.id: s for s in cached}
            return cached

        sessions = await self.parser.fetch_and_parse()
        with self._lock:
            self._sessions_by_id = {s.id: s for s in sessions}
        return sessions

    def get_all_sessions(self) -> List[Session]:
        """Get all available sessions."""
        with self._lock:
            return list(self._sessions_by_id.values())

    def get_session_by_id(self, session_id: str) -> Optional[Session]:
        """Get a specific session by ID."""
        with self._lock:
            return self._sessions_by_id.get(session_id)

    def create_personal_agenda(self) -> PersonalAgenda:
        """Create a new browser-scoped personal agenda."""
        return PersonalAgenda()

    async def add_session_to_agenda(
        self, agenda: PersonalAgenda, session_id: str
    ) -> tuple[bool, Optional[str]]:
        """
        Add a session to a personal agenda.

        Returns:
            Tuple of (success, error_message)
        """
        # Ensure sessions are loaded
        if not self._sessions_by_id:
            await self.load_sessions()
        
        with self._lock:
            session = self._sessions_by_id.get(session_id)
            if not session:
                return False, f"Session not found: {session_id}"

            if session_id in agenda.sessions:
                return False, "Session already in agenda"

            overlapping = self._find_overlapping_sessions(agenda, session)
            if overlapping:
                overlapping_ids = ", ".join(s.id for s in overlapping)
                return False, f"Session overlaps with existing agenda session(s): {overlapping_ids}"

            agenda.sessions.append(session_id)
            logger.info("Added a session to a browser-scoped agenda")
            return True, None

    def remove_session_from_agenda(self, agenda: PersonalAgenda, session_id: str) -> bool:
        """Remove a session from a personal agenda."""
        with self._lock:
            if session_id in agenda.sessions:
                agenda.sessions.remove(session_id)
                logger.info("Removed a session from a browser-scoped agenda")
                return True

            return False

    def get_agenda_sessions(self, agenda: PersonalAgenda) -> List[Session]:
        """Get all sessions in a personal agenda."""
        with self._lock:
            sessions = []
            for session_id in agenda.sessions:
                session = self._sessions_by_id.get(session_id)
                if session:
                    sessions.append(session)

            sessions.sort(key=lambda s: s.start_time)
            return sessions

    def _find_overlapping_sessions(
        self, agenda: PersonalAgenda, new_session: Session
    ) -> List[Session]:
        """Find sessions in the agenda that overlap with the new session."""
        overlapping = []
        for session_id in agenda.sessions:
            session = self._sessions_by_id.get(session_id)
            if session and session.overlaps_with(new_session):
                overlapping.append(session)
        return overlapping

    def get_conflicts_for_session(self, agenda: PersonalAgenda, session_id: str) -> List[Session]:
        """Return overlapping agenda sessions for a selected session."""
        with self._lock:
            session = self._sessions_by_id.get(session_id)
            if not session:
                return []
            return self._find_overlapping_sessions(agenda, session)

    def get_agenda_conflicts(self, agenda: PersonalAgenda) -> Dict[str, List[Session]]:
        """Return all overlapping sessions grouped by session id."""
        conflicts: Dict[str, List[Session]] = {}
        agenda_sessions = self.get_agenda_sessions(agenda)
        for index, session in enumerate(agenda_sessions):
            for other_session in agenda_sessions[index + 1 :]:
                if not session.overlaps_with(other_session):
                    continue
                conflicts.setdefault(session.id, []).append(other_session)
                conflicts.setdefault(other_session.id, []).append(session)
        return conflicts

    async def import_agenda(self, session_ids: List[str]) -> tuple[bool, Optional[str]]:
        """
        Import a personal agenda from a list of session IDs.

        Returns:
            Tuple of (success, error_message)
        """
        # Ensure sessions are loaded
        if not self._sessions_by_id:
            await self.load_sessions()
        
        with self._lock:
            invalid_ids = []
            for session_id in session_ids:
                if session_id not in self._sessions_by_id:
                    invalid_ids.append(session_id)

            if invalid_ids:
                return False, f"Invalid session IDs: {', '.join(invalid_ids)}"

            imported_sessions = [self._sessions_by_id[session_id] for session_id in session_ids]
            for index, session in enumerate(imported_sessions):
                for other_session in imported_sessions[index + 1 :]:
                    if session.overlaps_with(other_session):
                        return (
                            False,
                            f"Imported sessions overlaps: {session.id} and {other_session.id}",
                        )

            logger.info("Validated an imported browser-scoped agenda")
            return True, None

    def clear_agenda(self, agenda: PersonalAgenda) -> bool:
        """Clear all sessions from a personal agenda."""
        agenda.sessions.clear()
        logger.info("Cleared a browser-scoped agenda")
        return True
