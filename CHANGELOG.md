# Changelog

## [V1.3.200] - 2026-09-29
### Added
- CI/CD Intelligence (`CIIntelligence`) with failure signature hashing and max repair cycle protection (default 3 cycles).
- Pull Request Lifecycle Engine (`PRLifecycle`) aggregating Dependabot, Sonar, CodeRabbit, CodeQL, and Jules check states.
- Issue Triage Engine (`IssueTriage`) that automatically classifies issues (BUG, FEATURE, SECURITY) and computes dynamic priority based on label and age.
- Release Engineering (`ReleaseEngine`) that generates changelogs from parsed commit semantics and checks readiness.
- Fleet Anomalies and Action Journaling (`fleet_journal`).
- Remote Worker Engine (`WorkerRegistry`) for distributing capabilities (e.g. `docker`, `ollama`, `jules`) across nodes without exposing raw SSH access.
- Substantial Documentation updates (CI-CD.md, PULL-REQUESTS.md, ISSUES.md, RELEASES.md, REMOTE-WORKERS.md, AGENT-ROUTING.md, ARCHITECTURE.md).
