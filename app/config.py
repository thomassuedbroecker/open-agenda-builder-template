"""Application configuration."""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Open Agenda Builder Template"
    app_version: str = "1.1.0"
    app_description: str = (
        "Build personal agendas from a configurable event schedule using only open-source tooling."
    )
    debug: bool = False

    host: str = "0.0.0.0"
    port: int = 8082

    event_name: str = "Sample Event Program"
    event_day_label: str = "Program Day"
    event_date: str = "2026-04-15"
    event_timezone: str = "Europe/Berlin"
    agenda_label: str = "My Agenda"

    schedule_file: str = "app/data/sample-sessions.json"
    track_filter: str = ""
    start_time: str = "09:00"
    end_time: str = "18:00"
    data_source_name: str = "Bundled JSON schedule"

    agenda_cookie_name: str = "agenda_state"
    agenda_cookie_session_only: bool = True
    agenda_cookie_max_age_seconds: int = 604800
    secure_cookie: bool = False

    cache_ttl_seconds: int = 3600

    @field_validator("debug", "secure_cookie", "agenda_cookie_session_only", mode="before")
    @classmethod
    def parse_boolean_flags(cls, value: object) -> bool:
        """Parse tolerant boolean flags from environment variables."""
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on", "debug"}:
                return True
            if normalized in {"0", "false", "no", "off", "", "release", "prod", "production"}:
                return False
        return False

settings = Settings()
