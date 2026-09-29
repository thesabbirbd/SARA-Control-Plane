with open("app/main.py", "r") as f:
    content = f.read()

content = content.replace("        import subprocess\nfrom sara.security.risk import classify_command, RiskLevel\nfrom sara.security.redaction import redact", "        import subprocess")
content = "from sara.security.risk import classify_command, RiskLevel\nfrom sara.security.redaction import redact\n" + content

with open("app/main.py", "w") as f:
    f.write(content)
