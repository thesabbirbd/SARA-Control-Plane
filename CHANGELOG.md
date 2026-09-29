# Changelog

## [V1.4.50] - 2026-09-29
### Added
- **Supervisor Core**: `SupervisorService` mapping user objectives to graph-based task plans with strict state machines (RECEIVED to COMPLETED) and cycle-detection constraints.
- **Multi-Agent System**: `MultiAgentRouter` matching `CODER`, `TESTER`, and `REVIEWER` roles dynamically against agent provider capabilities.
- **Intelligent Memory**: `MemoryStore` enforcing bounded retrieval (`MAX_CONTEXT_BYTES`) and context trust leveling against prompt injections.
- **Deployment Orchestrator**: `DeploymentEngine` enforcing strict readiness gates and immediate rollbacks based on post-deploy health checks.
- **Remote Workers & Autonomy**: `WorkerDispatcher` executing capability and load-aware routing (CPU/RAM metrics), safeguarded by `AutonomyGovernor` hard limits to prevent infinite loops.
- **Tests**: 100% End-to-End coverage added for the V1.4.50 objectives suite.
- **Documentation**: New architecture specifications explicitly covering Autonomy, Deployments, Multi-Agent Routing, Memory, and Workflows.
