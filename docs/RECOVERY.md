# Failure Recovery & Chaos Engineering
SARA includes a durable recovery mechanism (Phase 7). `ChaosEngine` can inject deterministic faults (e.g. SSH disconnects) to ensure `DeploymentTransaction` captures failures, emits `deployment.failed` events over `EventBus`, and cascades into the state machine's `ROLLING_BACK` state safely.
