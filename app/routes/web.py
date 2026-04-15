"""Web routes for serving HTML pages."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.models.personal_agenda import PersonalAgenda
from app.services.agenda_service import AgendaService
from app.dependencies import get_agenda, get_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["web"])

# Templates
templates = Jinja2Templates(directory="app/templates")


def build_template_context(request: Request) -> dict[str, Any]:
    """Build common template context."""
    return {
        "request": request,
        "app_name": settings.app_name,
        "event_name": settings.event_name,
        "event_day_label": settings.event_day_label,
        "event_date": settings.event_date,
        "agenda_label": settings.agenda_label,
        "time_window": f"{settings.start_time} - {settings.end_time}",
        "track_filter": settings.track_filter,
        "data_source_name": settings.data_source_name,
        "agenda_cookie_name": settings.agenda_cookie_name,
    }


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    agenda: PersonalAgenda = Depends(get_agenda),
    service: AgendaService = Depends(get_service),
) -> Any:
    """Main page with the event agenda builder."""
    try:
        sessions = await service.load_sessions()
        context = build_template_context(request)
        context.update(
            {
                "sessions": sessions,
                "total_sessions": len(sessions),
            }
        )
        return templates.TemplateResponse(
            request,
            "index.html",
            context,
        )
    except Exception as e:
        logger.error(f"Error loading index page: {e}")
        context = build_template_context(request)
        context["error"] = str(e)
        return templates.TemplateResponse(
            request,
            "error.html",
            context,
            status_code=500,
        )


@router.get("/my-agenda", response_class=HTMLResponse)
async def my_agenda(
    request: Request,
    agenda: PersonalAgenda = Depends(get_agenda),
    service: AgendaService = Depends(get_service),
) -> Any:
    """Personal agenda view."""
    try:
        await service.load_sessions()
        sessions = service.get_agenda_sessions(agenda)
        context = build_template_context(request)
        context.update(
            {
                "sessions": sessions,
                "total_sessions": len(sessions),
            }
        )
        return templates.TemplateResponse(
            request,
            "my_agenda.html",
            context,
        )
    except Exception as e:
        logger.error(f"Error loading my agenda page: {e}")
        context = build_template_context(request)
        context["error"] = str(e)
        return templates.TemplateResponse(
            request,
            "error.html",
            context,
            status_code=500,
        )
