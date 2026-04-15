"""Parser for loading event schedule data from a JSON file."""

import json
import logging
from datetime import time
from pathlib import Path
from typing import List, Optional

from app.config import settings
from app.models.session import Session

logger = logging.getLogger(__name__)


class ParsingError(Exception):
    """Raised when parsing fails."""

    pass


class AgendaParser:
    """Parses event agenda data from a local JSON file."""

    def __init__(self) -> None:
        """Initialize the parser."""
        self.schedule_file = settings.schedule_file
        self.track_filter = settings.track_filter
        self.start_time = self._parse_time(settings.start_time)
        self.end_time = self._parse_time(settings.end_time)
        self._cache: Optional[List[Session]] = None

    @staticmethod
    def _parse_time(time_str: str) -> time:
        """Parse time string in HH:MM format."""
        try:
            hours, minutes = map(int, time_str.split(":"))
            return time(hour=hours, minute=minutes)
        except (ValueError, AttributeError) as e:
            raise ParsingError(f"Invalid time format: {time_str}") from e

    def _normalize_file_session(self, raw_data: dict) -> Optional[Session]:
        """Normalize session data loaded from a JSON schedule file."""
        try:
            session_id = str(raw_data.get("id", "")).strip()
            name = str(raw_data.get("name", "")).strip()
            start_time_str = str(raw_data.get("start_time", "")).strip()
            end_time_str = str(raw_data.get("end_time", "")).strip()

            if not all([session_id, name, start_time_str, end_time_str]):
                logger.debug("Skipping schedule entry with missing required fields")
                return None

            track = str(raw_data.get("track", "")).strip()
            if self.track_filter and track != self.track_filter:
                return None

            return Session(
                id=session_id,
                name=name,
                start_time=self._parse_time(start_time_str),
                end_time=self._parse_time(end_time_str),
                stage=str(raw_data.get("stage", "")).strip(),
                speaker=str(raw_data.get("speaker", "")).strip() or "TBA",
                format=str(raw_data.get("format", "")).strip() or "Session",
                topic=str(raw_data.get("topic", "")).strip() or "General",
                location=str(raw_data.get("location", "")).strip() or None,
                description=str(raw_data.get("description", "")).strip() or None,
            )
        except Exception as e:
            logger.warning(f"Failed to normalize schedule entry: {e}")
            return None

    def _filter_sessions(self, sessions: List[Session]) -> List[Session]:
        """Filter sessions for the configured time range."""
        filtered = []
        for session in sessions:
            if session.start_time >= self.start_time and session.end_time <= self.end_time:
                filtered.append(session)

        logger.info(
            f"Filtered {len(filtered)} sessions from {len(sessions)} "
            f"(time range: {self.start_time}-{self.end_time})"
        )
        return filtered

    def _load_schedule_file(self) -> List[Session]:
        """Load session data from the configured JSON schedule file."""
        if not self.schedule_file:
            raise ParsingError("No schedule file configured")

        schedule_path = Path(self.schedule_file)
        if not schedule_path.exists():
            raise ParsingError(f"Schedule file not found: {schedule_path}")

        try:
            with schedule_path.open("r", encoding="utf-8") as handle:
                raw_sessions = json.load(handle)
        except json.JSONDecodeError as e:
            raise ParsingError(f"Invalid JSON in schedule file: {e}") from e
        except OSError as e:
            raise ParsingError(f"Failed to read schedule file: {e}") from e

        if not isinstance(raw_sessions, list):
            raise ParsingError("Schedule file must contain a JSON array")

        sessions = []
        for raw_session in raw_sessions:
            if not isinstance(raw_session, dict):
                continue
            session = self._normalize_file_session(raw_session)
            if session:
                sessions.append(session)

        logger.info(
            "Parsed %s sessions from %s",
            len(sessions),
            schedule_path,
        )
        return sessions

    async def fetch_and_parse(self) -> List[Session]:
        """Load and parse the event agenda."""
        try:
            sessions = self._load_schedule_file()
            filtered_sessions = self._filter_sessions(sessions)
            filtered_sessions.sort(key=lambda s: s.start_time)
            self._cache = filtered_sessions
            return filtered_sessions
        except Exception as e:
            logger.error(f"Unexpected error parsing agenda: {e}")
            raise ParsingError(f"Failed to parse agenda: {e}") from e

    def get_cached_sessions(self) -> Optional[List[Session]]:
        """Get cached sessions if available."""
        return self._cache

    def clear_cache(self) -> None:
        """Clear the cached sessions."""
        self._cache = None
