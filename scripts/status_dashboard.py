#!/usr/bin/env python3
import os
import sqlite3
import psutil
from datetime import datetime
import subprocess
import shutil

DB_PATH = "/home/thesabbir/Documents/RPA Projects/sabbiR-control-plane/queue.db"

def get_system_stats():
    cpu = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return cpu, ram.percent, disk.percent

def check_service(name, cmd):
    try:
        subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return "🟢 ONLINE"
    except Exception:
        return "🔴 OFFLINE"

def check_bin(name):
    return "🟢 READY" if shutil.which(name) else "🔴 UNAVAILABLE"

def main():
    cpu, ram, disk = get_system_stats()
    
    # Check services
    worker_status = check_service("Worker", "systemctl --user is-active sabbir-bot")
    gemini_key = os.environ.get("GEMINI_API_KEY", "MISSING")
    gemini_status = check_service("Gemini", f"curl -s 'https://generativelanguage.googleapis.com/v1beta/models?key={gemini_key}' > /dev/null")
    agy_status = "🟢 READY" if os.path.exists("/snap/bin/agy") or shutil.which("agy") else "🔴 UNAVAILABLE"
    
    print("══════════════════════════════════════════════")
    print("       SABBiR CONTROL PLANE")
    print("══════════════════════════════════════════════")
    print("\nSYSTEM")
    print(f"  Worker       {worker_status}")
    print(f"  Gemini       {gemini_status}")
    print(f"  Antigravity  {agy_status}")
    print(f"  CPU: {cpu}%   RAM: {ram}%   Disk: {disk}%")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Current Task
        cursor.execute("SELECT * FROM tasks WHERE status IN ('RUNNING', 'STARTING')")
        current_tasks = cursor.fetchall()
        
        print("\nCURRENT TASK")
        if current_tasks:
            for t in current_tasks:
                if t['started_at']:
                    # SQLite started_at is string like '2023-10-10 12:00:00'
                    try:
                        started = datetime.strptime(t['started_at'], "%Y-%m-%d %H:%M:%S")
                        runtime = str(datetime.now() - started).split('.')[0]
                    except:
                        runtime = "Unknown"
                else:
                    runtime = "Starting..."
                    
                print(f"  #{t['id']}")
                print(f"  {t['project_name']}")
                print(f"  PID: {t['pid']}")
                print(f"  Runtime: {runtime}")
        else:
            print("  ⚪ IDLE")
            
        # Queue
        cursor.execute("SELECT * FROM tasks WHERE status IN ('PENDING', 'RUNNING') ORDER BY created_at ASC LIMIT 5")
        queue = cursor.fetchall()
        
        print("\nQUEUE")
        if queue:
            for q in queue:
                icon = "▶" if q['status'] == 'RUNNING' else "⏳"
                print(f"  {icon} #{q['id']} {q['project_name']} ({q['status']})")
        else:
            print("  (Empty)")
            
        conn.close()
    except Exception as e:
        print("\nDatabase Error:", e)

    print("══════════════════════════════════════════════")

if __name__ == "__main__":
    main()
