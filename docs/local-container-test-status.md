# Local Container Test Status

- Status: `PASS`
- Executed at (UTC): `2026-04-15T19:32:34Z`
- Base URL: `http://127.0.0.1:18082`

## Checks

- `health`: `PASS` - Health endpoint responded with healthy status
- `sessions`: `PASS` - Loaded 5 sessions from the container
- `agenda-add`: `PASS` - Added session `opening-remarks`
- `agenda-read`: `PASS` - Primary browser session retained its agenda
- `session-isolation`: `PASS` - Separate browser cookies receive separate agendas
- `export-json`: `PASS` - JSON export contains generic event metadata
- `branding`: `PASS` - Agenda page is free of legacy AI-conference branding
