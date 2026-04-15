"""API and web routes."""

from app.routes.api import router as api_router
from app.routes.web import router as web_router

__all__ = ["api_router", "web_router"]
