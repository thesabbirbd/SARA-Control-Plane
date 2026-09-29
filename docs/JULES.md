# Jules Integration

Jules acts as an asynchronous worker for SARA.
- **Task Creation**: SARA provisions a Jules session when CI/Sonar/Dependabot workflows require complex repairs.
- **Conflict Prevention**: Jules tasks are branched independently. SARA limits Jules repair cycles to `MAX_REPAIR_CYCLES=3` to prevent infinite loops.
- **Credentials**: Jules tokens are securely stored in the environment, never committed to `.github`.
