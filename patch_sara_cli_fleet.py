with open("sara/cli/main.py", "r") as f:
    content = f.read()

github_parser_str = """
    github_parser = subparsers.add_parser("github", help="GitHub Operations")
    github_subparsers = github_parser.add_subparsers(dest="gh_cmd")
    
    gh_fleet = github_subparsers.add_parser("fleet", help="Manage GitHub Fleet")
    gh_fleet.add_argument("--dry-run", action="store_true", help="Preview fleet changes")
    
    gh_id = github_subparsers.add_parser("identity", help="Check GitHub Identity")
"""

if "github_parser =" not in content:
    content = content.replace('    ctx_parser.add_argument("project", help="Project name")', '    ctx_parser.add_argument("project", help="Project name")\n' + github_parser_str)

github_logic = """
    elif args.command == "github":
        import asyncio
        from sara.github.provider import GitHubProvider
        from sara.github.fleet import FleetManager
        
        provider = GitHubProvider()
        
        if args.gh_cmd == "identity":
            ident = asyncio.run(provider.get_identity())
            print(f"GitHub: {'🟢' if ident['status'] == 'Connected' else '🔴'} {ident['status']}")
            print(f"Account: {ident['user']}")
        elif args.gh_cmd == "fleet":
            fleet = FleetManager(provider)
            stats = asyncio.run(fleet.analyze_fleet())
            print("🐙 GITHUB ENGINEERING REPORT")
            print(f"Repos: {stats['total_repos']} discovered")
            print(f"Dependabot: {stats['dependabot_configured']} configured")
            print(f"CodeRabbit: {stats['coderabbit_connected']} connected")
            print(f"Sonar: {stats['sonar_connected']} connected")
            print(f"Jules: {'AVAILABLE' if stats['jules_available'] else 'NOT CONFIGURED'}")
            
            if args.dry_run:
                print("\\n[DRY RUN] Would evaluate repository policies without mutating.")
        return 0
"""

if 'args.command == "github"' not in content:
    content = content.replace('    else:\n        parser.print_help()', github_logic + '    else:\n        parser.print_help()')

with open("sara/cli/main.py", "w") as f:
    f.write(content)
