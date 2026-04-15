# Code Section

The application code lives in this directory.

## Structure

- `config.py`: runtime configuration and environment variable handling
- `main.py`: FastAPI application setup and middleware
- `dependencies.py`: shared dependency providers
- `models/`: Pydantic models for sessions and agenda exports
- `services/`: schedule parsing and agenda business logic
- `routes/`: API and HTML route handlers
- `templates/`: Jinja templates
- `static/`: CSS and JavaScript assets
- `data/`: bundled sample schedule data

## Design Notes

- The code is event-generic and no longer tied to a specific conference
- Session data is loaded from a local JSON file
- Concurrent users are isolated with an anonymous essential cookie
- No database or personal profile storage is used

For the broader system design, see [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md).
