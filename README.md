
## Remote Usage
Interact with the bot on Telegram. Use the persistent dashboard keyboard, or standard commands:
- `/ag <project> <instruction>` - Run a task
- `/projects` - List available projects
- `/tasks` - View queue
- `/status` - Check system health

## Local Monitoring
To observe tasks in real-time from the machine:
```bash
./scripts/live_console.sh
```
This opens a `tmux` session with the Service Log, Current Task Log, and System Dashboard.

### Logs
All task logs are stored persistently in:
```text
data/logs/
```

### Service Logs
```bash
journalctl --user -u sara -f
```

### Task Log
To tail a specific task:
```bash
./scripts/task_log.sh <id>
```

### Current Task
```bash
python3 ./scripts/current_task.sh
```
