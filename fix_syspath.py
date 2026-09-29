with open("app/main.py", "r") as f:
    content = f.read()

prefix = """import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
content = prefix + content

with open("app/main.py", "w") as f:
    f.write(content)
