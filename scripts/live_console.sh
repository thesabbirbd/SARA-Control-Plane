#!/usr/bin/env bash

SESSION_NAME="sara-console"
PROJECT_DIR="/home/thesabbir/Documents/RPA Projects/project-sara"

if ! command -v tmux &> /dev/null; then
    echo "tmux is not installed. Please install it with: sudo apt install tmux"
    exit 1
fi

chmod +x "$PROJECT_DIR/scripts/status.sh"
chmod +x "$PROJECT_DIR/scripts/task_log.sh"
chmod +x "$PROJECT_DIR/scripts/auto_tail.sh"

# Check if session exists
tmux has-session -t "$SESSION_NAME" 2>/dev/null

if [ $? != 0 ]; then
    # Create new session in background
    tmux new-session -d -s "$SESSION_NAME" -c "$PROJECT_DIR"
    
    # Pane 1 (Top): Service Log
    tmux send-keys -t "$SESSION_NAME:0" "journalctl --user -u sara.service -f" C-m
    
    # Split horizontally (Top / Bottom)
    tmux split-window -h -t "$SESSION_NAME:0"
    
    # Bottom Left: Auto Tail
    tmux send-keys -t "$SESSION_NAME:0.1" "./scripts/auto_tail.sh" C-m
    
    # Split Bottom Pane vertically
    tmux split-window -v -t "$SESSION_NAME:0.1"
    
    # Bottom Right: Dashboard
    tmux send-keys -t "$SESSION_NAME:0.2" "watch -n 2 -c ./scripts/status.sh" C-m
    
    # Adjust pane sizes (make bottom row smaller if needed)
    tmux resize-pane -t "$SESSION_NAME:0.0" -R 20
fi

# Attach to session
tmux attach -t "$SESSION_NAME"
