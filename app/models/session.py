"""Session model representing a single event session."""

from datetime import time
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Session(BaseModel):
    """Represents a single event session."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "opening-remarks",
                "name": "Opening Remarks",
                "start_time": "10:00",
                "end_time": "10:30",
                "stage": "Main Stage",
                "speaker": "Program Team",
                "format": "Briefing",
                "topic": "Welcome",
                "location": "Hall A",
                "description": "Kickoff for the day.",
            }
        }
    )

    id: str = Field(..., description="Unique identifier (derived from slug)")
    name: str = Field(..., description="Session title")
    start_time: time = Field(..., description="Session start time")
    end_time: time = Field(..., description="Session end time")
    stage: str = Field(..., description="Physical location/stage")
    speaker: str = Field(..., description="Speaker name(s)")
    format: str = Field(..., description="Session format (Keynote, Workshop, etc.)")
    topic: str = Field(..., description="Topic category")
    location: Optional[str] = Field(None, description="Color-coded location")
    description: Optional[str] = Field(None, description="Session description")

    def overlaps_with(self, other: "Session") -> bool:
        """Check if this session overlaps with another session."""
        return not (self.end_time <= other.start_time or self.start_time >= other.end_time)

    def format_time_range(self) -> str:
        """Format the time range as a string."""
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
