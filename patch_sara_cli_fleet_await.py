with open("sara/cli/main.py", "r") as f:
    content = f.read()

content = content.replace("asyncio.run(provider.get_identity())", "await provider.get_identity()")
content = content.replace("asyncio.run(fleet.analyze_fleet())", "await fleet.analyze_fleet()")

with open("sara/cli/main.py", "w") as f:
    f.write(content)
