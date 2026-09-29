import argparse
import asyncio
import sys
from sara.database.core import get_db

async def run_cli():
    parser = argparse.ArgumentParser(prog="sara", description="SARA Control Plane CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    # Task commands
    task_parser = subparsers.add_parser("task", help="Manage tasks")
    task_subparsers = task_parser.add_subparsers(dest="task_cmd")
    
    task_subparsers.add_parser("list", help="List active tasks")
    
    args = parser.parse_args()
    
    if args.command == "task":
        if args.task_cmd == "list":
            async with await get_db() as db:
                async with db.execute("SELECT id, project_name, status FROM tasks WHERE status IN ('PENDING', 'RUNNING')") as c:
                    tasks = await c.fetchall()
                    if not tasks:
                        print("No active tasks.")
                    for t in tasks:
                        print(f"#{t['id']} [{t['status']}] {t['project_name']}")
        else:
            task_parser.print_help()
    else:
        parser.print_help()

def main():
    asyncio.run(run_cli())

if __name__ == "__main__":
    main()
