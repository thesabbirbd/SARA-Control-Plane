# Changelog

## [V1.3.100] - 2026-09-29
### Added
- Local Web Console & PWA Dashboard (`/api/stats`, `/api/tasks`, `/api/sessions`).
- Agent Runtime Unified Abstraction (`sara/runtime/core.py`).
- Project Context Builder with Git summarization and compression (`sara/context/builder.py`).
- CLI `context` command to view project runtime context bounds.
- Database tables for Operational Memory, Artifacts, and Workflow Policies.
- Uvicorn and FastAPI integrations for local-first headless dashboards.

### Changed
- Integrated web server directly into `sara.service` via `asyncio` task.
- Fixed unhandled `get_secret_value` exception on Pydantic models when running systemd service.
- Cleaned up loose temporary scripts from massive refactor rounds.

### Security
- Web console bound strictly to localhost (127.0.0.1:8080) by default to prevent external access.
- Safe access bounds for project contexts (defaults to `$SARA_WORKSPACE`).
