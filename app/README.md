# Application Code

Navigation: [Repository Root](../README.md) | [Architecture](../docs/ARCHITECTURE.md) | [Tests](../tests/README.md)

The application code lives in this directory.

## Table of Contents

1. [Purpose](#1-purpose)
2. [Structure](#2-structure)
3. [Design Notes](#3-design-notes)

## 1. Purpose

This package contains the FastAPI application, data models, service layer, templates, static assets, and bundled sample schedule data.

## 2. Structure

- `config.py`: runtime configuration and environment variable handling
- `main.py`: FastAPI application setup, middleware, and health endpoint
- `dependencies.py`: shared dependency providers and cookie serialization
- `models/`: Pydantic models for sessions and agenda exports
- `services/`: schedule parsing and agenda business logic
- `routes/`: API and HTML route handlers
- `templates/`: Jinja templates
- `static/`: CSS and JavaScript assets
- `data/`: bundled sample schedule data

## 3. Design Notes

- The code is event-generic and not tied to a specific conference
- Session data is loaded from a local JSON file
- Concurrent users are isolated with an anonymous essential cookie
- No database or personal profile storage is used

For the broader system design, see [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md).
