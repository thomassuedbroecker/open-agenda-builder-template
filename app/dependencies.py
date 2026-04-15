"""Shared dependencies for the application."""

import base64

from fastapi import Request

from app.models.personal_agenda import PersonalAgenda
from app.services.agenda_service import AgendaService

_service: AgendaService | None = None


def get_service() -> AgendaService:
    """Get or create the shared agenda service instance."""
    global _service
    if _service is None:
        _service = AgendaService()
    return _service


def serialize_agenda_cookie(agenda: PersonalAgenda) -> str:
    """Serialize agenda state for cookie storage."""
    encoded = base64.urlsafe_b64encode(agenda.model_dump_json().encode("utf-8")).decode("ascii")
    return encoded.rstrip("=")


def deserialize_agenda_cookie(raw_value: str | None) -> PersonalAgenda:
    """Deserialize agenda state from cookie storage."""
    if not raw_value:
        return PersonalAgenda()

    padded = raw_value + ("=" * (-len(raw_value) % 4))
    try:
        decoded = base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8")
        return PersonalAgenda.model_validate_json(decoded)
    except Exception:
        return PersonalAgenda()


def get_agenda(request: Request) -> PersonalAgenda:
    """Return the browser-scoped agenda stored on the request."""
    return request.state.agenda
