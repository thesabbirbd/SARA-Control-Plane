# Changelog

## [V1.3.150] - 2026-09-29
### Added
- GitHub DevSecOps Orchestrator and Fleet Manager.
- ONE PR = ONE PRIMARY WRITER concurrency lock (`PROrchestrator`).
- Dependabot, SonarQube Cloud, CodeRabbit, and Jules integrations.
- Fleet analysis with dry-run capabilities via `sara github fleet --dry-run`.
- Normalization and deduplication of AI and Security findings (`github_findings` schema).
- Documentation for DevSecOps, Jules, Dependabot, CodeRabbit, Sonar, Policies, and Fleet workflows.

### Security
- PR Locking strictly blocks multiple agent writers (e.g., CodeRabbit autofix + Jules repair) from causing race conditions.
- Default CodeRabbit behavior set to REVIEW-ONLY.
- GitHub Identity checks isolated and token redaction enforced.
