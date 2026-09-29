#!/usr/bin/env bash
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DB_PATH="${SARA_DB_PATH:-$PROJECT_ROOT/queue.db}"

CURRENT_LOG=""
TAIL_PID=""

cleanup() {
    if [ -n "$TAIL_PID" ]; then
        kill "$TAIL_PID" 2>/dev/null
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "Waiting for tasks..."

while true; do
    # Find running task ID
    TASK_ID=$(sqlite3 "$DB_PATH" "SELECT id FROM tasks WHERE status IN ('RUNNING', 'STARTING') ORDER BY id DESC LIMIT 1;")
    
    if [ -n "$TASK_ID" ]; then
        LOG_FILE="$PROJECT_ROOT/logs/task_${TASK_ID}.log"
        
        if [ "$CURRENT_LOG" != "$LOG_FILE" ]; then
            # New task found!
            if [ -n "$TAIL_PID" ]; then
                kill "$TAIL_PID" 2>/dev/null
            fi
            
            clear
            echo "=========================================="
            echo "       LIVE LOG: TASK #$TASK_ID           "
            echo "=========================================="
            
            if [ -f "$LOG_FILE" ]; then
                tail -F -n 50 "$LOG_FILE" &
                TAIL_PID=$!
            else
                echo "Log file not yet created: $LOG_FILE"
                TAIL_PID=""
            fi
            
            CURRENT_LOG="$LOG_FILE"
        fi
    else
        if [ "$CURRENT_LOG" != "IDLE" ]; then
            if [ -n "$TAIL_PID" ]; then
                kill "$TAIL_PID" 2>/dev/null
                TAIL_PID=""
            fi
            clear
            echo "=========================================="
            echo "                 IDLE                     "
            echo "       No active Antigravity task         "
            echo "=========================================="
            CURRENT_LOG="IDLE"
        fi
    fi
    
    sleep 2
done
