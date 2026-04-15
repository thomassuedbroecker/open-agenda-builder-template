"""Tests for the agenda parser."""

import json
from datetime import time

import pytest

from app.services.agenda_parser import AgendaParser, ParsingError


def test_parse_time():
    """Test time parsing."""
    parser = AgendaParser()

    assert parser._parse_time("10:00") == time(10, 0)
    assert parser._parse_time("14:30") == time(14, 30)
    assert parser._parse_time("09:15") == time(9, 15)


def test_parse_time_invalid():
    """Test invalid time parsing."""
    parser = AgendaParser()

    with pytest.raises(ParsingError):
        parser._parse_time("invalid")

    with pytest.raises(ParsingError):
        parser._parse_time("25:00")


def test_load_schedule_file(tmp_path):
    """Test loading sessions from a JSON schedule file."""
    schedule_path = tmp_path / "schedule.json"
    schedule_path.write_text(
        json.dumps(
            [
                {
                    "id": "opening-remarks",
                    "name": "Opening Remarks",
                    "start_time": "09:00",
                    "end_time": "09:30",
                    "stage": "Main Hall",
                    "speaker": "Program Team",
                    "format": "Briefing",
                    "topic": "Welcome",
                    "location": "Hall A",
                    "track": "General",
                },
                {
                    "id": "ops-workshop",
                    "name": "Operations Workshop",
                    "start_time": "10:00",
                    "end_time": "11:00",
                    "stage": "Room 1",
                    "speaker": "Operations Lead",
                    "format": "Workshop",
                    "topic": "Planning",
                    "location": "Room 1",
                    "track": "Operations",
                },
            ]
        ),
        encoding="utf-8",
    )

    parser = AgendaParser()
    parser.schedule_file = str(schedule_path)
    parser.track_filter = ""

    sessions = parser._load_schedule_file()

    assert len(sessions) == 2
    assert sessions[0].id == "opening-remarks"
    assert sessions[1].speaker == "Operations Lead"


def test_load_schedule_file_invalid_json(tmp_path):
    """Test invalid JSON handling."""
    schedule_path = tmp_path / "schedule.json"
    schedule_path.write_text("{invalid", encoding="utf-8")

    parser = AgendaParser()
    parser.schedule_file = str(schedule_path)

    with pytest.raises(ParsingError):
        parser._load_schedule_file()


def test_filter_sessions_by_track_and_time(tmp_path):
    """Test filtering sessions by track and time window."""
    schedule_path = tmp_path / "schedule.json"
    schedule_path.write_text(
        json.dumps(
            [
                {
                    "id": "early-general",
                    "name": "Early General Session",
                    "start_time": "08:00",
                    "end_time": "08:30",
                    "stage": "Main Hall",
                    "speaker": "Program Team",
                    "format": "Briefing",
                    "topic": "Setup",
                    "track": "General",
                },
                {
                    "id": "valid-general",
                    "name": "Valid General Session",
                    "start_time": "10:00",
                    "end_time": "11:00",
                    "stage": "Main Hall",
                    "speaker": "Program Team",
                    "format": "Briefing",
                    "topic": "Welcome",
                    "track": "General",
                },
                {
                    "id": "valid-ops",
                    "name": "Valid Ops Session",
                    "start_time": "10:00",
                    "end_time": "11:00",
                    "stage": "Room 1",
                    "speaker": "Operations Lead",
                    "format": "Workshop",
                    "topic": "Planning",
                    "track": "Operations",
                },
            ]
        ),
        encoding="utf-8",
    )

    parser = AgendaParser()
    parser.schedule_file = str(schedule_path)
    parser.track_filter = "General"
    parser.start_time = time(9, 0)
    parser.end_time = time(18, 0)

    sessions = parser._load_schedule_file()
    filtered = parser._filter_sessions(sessions)

    assert len(filtered) == 1
    assert filtered[0].id == "valid-general"
