#!/usr/bin/env python3
import sqlite3
import sys

DB_PATH = "/home/thesabbir/Documents/RPA Projects/project-sara/queue.db"

def main():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM tasks WHERE status IN ('RUNNING', 'STARTING')")
        tasks = cursor.fetchall()
        
        if tasks:
            for t in tasks:
                print(f"Task #{t['id']}")
                print(f"Project: {t['project_name']}")
                print(f"Status: {t['status']}")
                print(f"PID: {t['pid']}")
                if t['log_path']:
                    print(f"Log: {t['log_path']}")
        else:
            print("No task currently running.")
            
    except Exception as e:
        print("Error:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
