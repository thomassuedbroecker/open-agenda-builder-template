"""Main FastAPI application."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.dependencies import deserialize_agenda_cookie, serialize_agenda_cookie
from app.routes import api_router, web_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Schedule file: {settings.schedule_file}")
    logger.info(f"Track filter: {settings.track_filter or 'all'}")
    logger.info(f"Time range: {settings.start_time} - {settings.end_time}")
    yield
    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(api_router)
app.include_router(web_router)


@app.middleware("http")
async def attach_agenda_cookie(request: Request, call_next):
    """Attach a privacy-safe agenda cookie to each browser session."""
    original_cookie = request.cookies.get(settings.agenda_cookie_name)
    request.state.agenda = deserialize_agenda_cookie(original_cookie)

    response = await call_next(request)
    serialized_agenda = serialize_agenda_cookie(request.state.agenda)
    if original_cookie != serialized_agenda:
        cookie_options = {
            "key": settings.agenda_cookie_name,
            "value": serialized_agenda,
            "httponly": True,
            "samesite": "lax",
            "secure": settings.secure_cookie,
        }
        if not settings.agenda_cookie_session_only:
            cookie_options["max_age"] = settings.agenda_cookie_max_age_seconds
        response.set_cookie(**cookie_options)
    return response


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
