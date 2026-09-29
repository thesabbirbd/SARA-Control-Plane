import argparse
import asyncio
import sys
from sara.database.core import get_db

async def run_cli():
    parser = argparse.ArgumentParser(prog="sara", description="SARA Control Plane CLI")
    subparsers = parser.add_subparsers(dest="command")
    ctx_parser = subparsers.add_parser("context", help="Inspect project context")
    ctx_parser.add_argument("project", help="Project name")

    github_parser = subparsers.add_parser("github", help="GitHub Operations")
    github_subparsers = github_parser.add_subparsers(dest="gh_cmd")
    
    gh_fleet = github_subparsers.add_parser("fleet", help="Manage GitHub Fleet")
    gh_fleet.add_argument("--dry-run", action="store_true", help="Preview fleet changes")
    
    gh_id = github_subparsers.add_parser("identity", help="Check GitHub Identity")


    
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

    elif args.command == "context":
        from sara.context.builder import ProjectContextBuilder
        import json
        builder = ProjectContextBuilder("/home/thesabbir/Documents/RPA Projects", args.project)
        print(json.dumps(builder.build_context(), indent=2))
        return 0

    elif args.command == "github":
        import asyncio
        from sara.github.provider import GitHubProvider
        from sara.github.fleet import FleetManager
        
        provider = GitHubProvider()
        
        if args.gh_cmd == "identity":
            ident = await provider.get_identity()
            print(f"GitHub: {'🟢' if ident['status'] == 'Connected' else '🔴'} {ident['status']}")
            print(f"Account: {ident['user']}")
        elif args.gh_cmd == "fleet":
            fleet = FleetManager(provider)
            stats = await fleet.analyze_fleet()
            print("🐙 GITHUB ENGINEERING REPORT")
            print(f"Repos: {stats['total_repos']} discovered")
            print(f"Dependabot: {stats['dependabot_configured']} configured")
            print(f"CodeRabbit: {stats['coderabbit_connected']} connected")
            print(f"Sonar: {stats['sonar_connected']} connected")
            print(f"Jules: {'AVAILABLE' if stats['jules_available'] else 'NOT CONFIGURED'}")
            
            if args.dry_run:
                print("\n[DRY RUN] Would evaluate repository policies without mutating.")
        return 0
    else:
        parser.print_help()

def main():
    asyncio.run(run_cli())

if __name__ == "__main__":
    main()
