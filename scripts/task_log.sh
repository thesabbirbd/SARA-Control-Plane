#!/usr/bin/env bash

if [ -z "$1" ]; then
    echo "Usage: ./task_log.sh <id>"
    exit 1
fi

TASK_ID=$1
LOG_FILE="/home/thesabbir/Documents/RPA Projects/project-sara/logs/task_${TASK_ID}.log"

echo "======================================"
echo "    FOLLOWING TASK #$TASK_ID LOG      "
echo "======================================"

if [ -f "$LOG_FILE" ]; then
    tail -F "$LOG_FILE"
else
    echo "⚠️ Log file not found: $LOG_FILE"
    echo "Waiting for it to be created..."
    
    # Wait for the file to be created, checking every 1s
    while [ ! -f "$LOG_FILE" ]; do
        sleep 1
    done
    
    tail -F "$LOG_FILE"
fi
