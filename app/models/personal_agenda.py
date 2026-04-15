"""Personal agenda model."""

from datetime import UTC, datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class PersonalAgenda(BaseModel):
    """Represents a user's personal agenda."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "version": "1.0",
                "created_at": "2026-04-15T10:00:00Z",
                "sessions": ["opening-remarks", "customer-workshop"],
            }
        }
    )

    version: str = Field(default="1.0", description="Schema version")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Creation timestamp"
    )
    sessions: List[str] = Field(
        default_factory=list, description="List of selected session IDs"
    )

class PersonalAgendaExport(BaseModel):
    """Export format for personal agenda with full session details."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "version": "1.0",
                "created_at": "2026-04-15T10:00:00Z",
                "exported_at": "2026-04-15T10:05:00Z",
                "event_name": "Sample Event Program",
                "event_date": "2026-04-15",
                "session_ids": ["opening-remarks", "customer-workshop"],
            }
        }
    )

    version: str = Field(default="1.0", description="Schema version")
    created_at: datetime = Field(..., description="Creation timestamp")
    exported_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Export timestamp"
    )
    event_name: str = Field(default="Sample Event Program", description="Event name")
    event_date: str = Field(default="2026-04-15", description="Event date")
    session_ids: List[str] = Field(..., description="List of selected session IDs")
