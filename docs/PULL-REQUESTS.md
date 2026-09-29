# Pull Request Lifecycle
The `PRLifecycle` engine aggregates CI, Sonar, CodeRabbit, and Jules into a single state machine.
Valid states: OPEN, CI_RUNNING, REVIEW_RUNNING, QUALITY_CHECK, NEEDS_FIX, READY_FOR_HUMAN.
