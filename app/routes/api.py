"""REST API endpoints."""

import json
import logging
from datetime import UTC, datetime
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse, Response
from icalendar import Calendar, Event

from app.config import settings
from app.dependencies import get_agenda, get_service
from app.models.personal_agenda import PersonalAgenda, PersonalAgendaExport
from app.models.session import Session
from app.services.agenda_service import AgendaService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/sessions", response_model=List[Session])
async def get_sessions(service: AgendaService = Depends(get_service)) -> List[Session]:
    """Get all available sessions in the configured schedule window."""
    try:
        sessions = await service.load_sessions()
        return sessions
    except Exception as e:
        logger.error(f"Error loading sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load sessions: {str(e)}")


@router.post("/agenda/add")
async def add_session(
    session_id: str,
    agenda: PersonalAgenda = Depends(get_agenda),
    service: AgendaService = Depends(get_service),
) -> dict:
    """Add a session to the personal agenda."""
    success, error = await service.add_session_to_agenda(agenda, session_id)
    
    if not success:
        raise HTTPException(status_code=400, detail=error)

    conflicts = service.get_conflicts_for_session(agenda, session_id)
    return {
        "success": True,
        "message": "Session added successfully",
        "conflicts": [session.name for session in conflicts],
    }


@router.delete("/agenda/remove/{session_id}")
async def remove_session(
    session_id: str,
    agenda: PersonalAgenda = Depends(get_agenda),
    service: AgendaService = Depends(get_service),
) -> dict:
    """Remove a session from the personal agenda."""
    success = service.remove_session_from_agenda(agenda, session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found in agenda")
    
    return {"success": True, "message": "Session removed successfully"}


@router.get("/agenda/sessions", response_model=List[Session])
async def get_agenda_sessions(
    agenda: PersonalAgenda = Depends(get_agenda),
    service: AgendaService = Depends(get_service),
) -> List[Session]:
    """Get all sessions in the personal agenda."""
    await service.load_sessions()
    return service.get_agenda_sessions(agenda)


@router.get("/agenda/export/json")
async def export_json(
    agenda: PersonalAgenda = Depends(get_agenda),
    service: AgendaService = Depends(get_service),
) -> Response:
    """Export personal agenda as JSON."""
    if not agenda.sessions:
        raise HTTPException(status_code=404, detail="Agenda is empty")
    
    export = PersonalAgendaExport(
        created_at=agenda.created_at,
        event_name=settings.event_name,
        event_date=settings.event_date,
        session_ids=agenda.sessions,
    )
    
    return JSONResponse(
        content=export.model_dump(mode="json"),
        headers={
            "Content-Disposition": f"attachment; filename=agenda_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        },
    )


@router.get("/agenda/export/ics")
async def export_ics(
    agenda: PersonalAgenda = Depends(get_agenda),
    service: AgendaService = Depends(get_service),
) -> Response:
    """Export personal agenda as ICS calendar file."""
    await service.load_sessions()
    sessions = service.get_agenda_sessions(agenda)
    
    if not sessions:
        raise HTTPException(status_code=404, detail="No sessions in agenda")
    
    # Create calendar
    cal = Calendar()
    cal.add("prodid", f"-//{settings.app_name}//EN")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("method", "PUBLISH")
    cal.add("x-wr-calname", f"{settings.event_name} - {settings.agenda_label}")
    cal.add("x-wr-timezone", settings.event_timezone)
    
    event_date = datetime.strptime(settings.event_date, "%Y-%m-%d").date()
    
    # Add events
    for session in sessions:
        event = Event()
        event.add("summary", session.name)
        event.add("dtstart", datetime.combine(event_date, session.start_time))
        event.add("dtend", datetime.combine(event_date, session.end_time))
        event.add("location", f"{session.stage} ({session.location})" if session.location else session.stage)
        event.add("description", f"Speaker: {session.speaker}\nFormat: {session.format}\nTopic: {session.topic}")
        event.add("uid", f"{session.id}@agenda-builder.local")
        cal.add_component(event)
    
    # Generate ICS content
    ics_content = cal.to_ical()
    
    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f"attachment; filename=agenda_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ics"
        },
    )


@router.post("/agenda/import")
async def import_agenda(
    file: UploadFile = File(...),
    agenda: PersonalAgenda = Depends(get_agenda),
    service: AgendaService = Depends(get_service),
) -> dict:
    """Import personal agenda from JSON file."""
    try:
        # Read and parse JSON
        content = await file.read()
        data = json.loads(content)
        
        # Validate schema
        if "version" not in data or "session_ids" not in data:
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON format. Expected 'version' and 'session_ids' fields."
            )
        
        # Check version compatibility
        if data["version"] != "1.0":
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported schema version: {data['version']}. Expected 1.0"
            )
        
        # Import sessions
        session_ids = data["session_ids"]
        success, error = await service.import_agenda(session_ids)
        
        if not success:
            raise HTTPException(status_code=400, detail=error)

        agenda.sessions = session_ids
        agenda.created_at = datetime.now(UTC)
        
        return {
            "success": True,
            "message": f"Successfully imported {len(session_ids)} sessions",
            "session_count": len(session_ids),
        }
    except HTTPException:
        raise
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    except Exception as e:
        logger.error(f"Error importing agenda: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to import agenda: {str(e)}")


@router.delete("/agenda/clear")
async def clear_agenda(
    agenda: PersonalAgenda = Depends(get_agenda),
    service: AgendaService = Depends(get_service),
) -> dict:
    """Clear all sessions from the personal agenda."""
    success = service.clear_agenda(agenda)
    
    return {"success": True, "message": "Agenda cleared successfully"}
