# SARA DevSecOps Orchestration

SARA V1.3.150 introduces a governed software-delivery pipeline enforcing the **ONE PR = ONE PRIMARY CODING WRITER** policy.

## Architecture
- **SARA** acts as the overarching Policy Engine and PR State Machine.
- **Dependabot**: Dependency updates.
- **CodeRabbit**: AI code review and verification.
- **SonarQube Cloud**: Static code analysis and quality gates.
- **Jules**: Asynchronous coding agent (handles complex multi-file repairs).
- **CodeQL**: Security analysis.

## Conflict Prevention
When Dependabot triggers a CI failure, SARA captures the `DEPENDABOT_FAILED` event. CodeRabbit and Sonar analyze the failure. If actionable, SARA issues a repair task to Jules, which creates a *controlled branch* to avoid mutating Dependabot's branch directly. 

PR Locks prevent CodeRabbit Autofix and Jules from modifying the same PR concurrently.
