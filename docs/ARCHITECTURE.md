# Architecture

## Overview

Open Agenda Builder Template is a local-first FastAPI application for building personal agendas from a configurable event schedule. The current architecture is designed for longer-term internal or cross-company reuse rather than one-off prototype usage.

## Core Design Decisions

### 1. Generic Event Metadata

The application no longer hardcodes any conference or company identity. Event name, date, timezone, labels, schedule source, track filter, and time window are all configuration-driven.

### 2. Local JSON Schedule Source

The supported source of truth is a local JSON file.

Why:

- Deterministic behavior
- No dependency on external websites
- Easier testing
- Better privacy posture
- Lower legal risk from copying live third-party content

The bundled sample schedule is neutralized and avoids personal data.

### 3. Concurrent Browser Usage

Each browser stores its agenda state in one essential session cookie. The application process stays stateless with respect to user-specific agenda data.

Properties:

- Concurrent users do not overwrite each other
- No login or personal profile is required
- The cookie contains only serialized agenda state
- The cookie is session-scoped by default and expires when the browser session ends
- Restart does not invalidate already stored browser agendas
- Horizontal scaling is simpler because user-specific state is not stored in process memory

### 4. Local-First Privacy Model

The application is intentionally minimal:

- No analytics
- No external tracking
- No user registration
- No third-party assets
- No persistent database

This is privacy-by-design oriented, but legal compliance still depends on deployment context.

### 5. Single-Container Runtime

The application serves API, templates, static assets, and export endpoints from one FastAPI container. This keeps operation simple and makes the local-container smoke test representative of real usage.

### 6. Twelve-Factor Alignment

The implementation is aligned to the twelve-factor methodology where it materially applies:

- Codebase: one tracked codebase
- Dependencies: explicit dependency files and project metadata
- Config: environment-driven settings
- Backing services: file path and runtime endpoints are attached through config
- Build, release, run: separated into image build, runtime config, and execution scripts
- Processes: user agenda state is not stored in process memory
- Port binding: the app binds directly to its configured port
- Concurrency: concurrent users are isolated without shared process state
- Disposability: the process can be restarted without losing bundled configuration
- Dev/prod parity: the same container image shape is used locally and in CI
- Logs: application logs go to stdout/stderr
- Admin processes: verification and maintenance commands are one-off scripts

## Component Map

### `app/config.py`

Defines generic runtime configuration for:

- Event metadata
- Schedule file path
- Time filtering
- Cookie behavior
- Host and port

### `app/services/agenda_parser.py`

Loads and validates session data from the configured JSON schedule file, applies optional track filtering, applies the configured time window, and caches the normalized session catalog in memory.

### `app/services/agenda_service.py`

Handles:

- Agenda creation
- Overlap detection
- Import validation
- Export preparation
- Stateless multi-user agenda evaluation

The service uses a re-entrant lock to protect the shared session catalog cache. User-specific agenda state is passed in from the cookie-backed request context.

### `app/routes/api.py`

Exposes:

- Session listing
- Add/remove/clear agenda operations
- JSON export
- ICS export
- JSON import

All agenda endpoints resolve the active browser agenda from middleware rather than a shared `default` agenda or process-local session map.

### `app/routes/web.py`

Renders:

- Shared program page
- Personal agenda page
- Error page

Template context is built from the current configuration and the active cookie-backed agenda.

### `app/main.py`

Provides:

- FastAPI app setup
- Static file mounting
- CORS middleware
- Cookie-backed agenda middleware
- Health endpoint

## Data Flow

### Session Loading

`JSON schedule file -> parser normalization -> optional track filter -> time window filter -> cache -> API/UI`

### Agenda Selection

`browser action -> JS fetch -> API route -> agenda service -> overlap validation -> cookie-backed agenda update -> refreshed UI`

### Export

`cookie-backed agenda -> export model / iCalendar generation -> browser download`

## Testing Strategy

The project keeps test scope aligned to supported runtime behavior.

### Python Tests

`tests/test_parser.py`

- Time parsing
- JSON schedule loading
- Invalid JSON handling
- Track and time filtering

`tests/test_service.py`

- Agenda creation
- Overlap handling
- Import validation
- Clear/remove behavior

`tests/test_api.py`

- Health endpoint
- Session retrieval
- Agenda CRUD
- Import validation
- Export metadata
- Browser isolation via separate cookie jars and stateless cookie-backed agendas

### Local Container Smoke Test

`scripts/run-local-container-tests.sh` builds and runs the container locally, then calls `testing/local_container_smoke_test.py`.

This is the authoritative deployment verification path for the repository.

## Current Constraints

- Browser agendas are cookie-scoped and not shared across devices
- No authenticated collaboration
- No database-backed retention or audit trail
- Large agendas are limited by practical cookie size constraints

Those constraints are intentional for the current privacy and operational profile.
