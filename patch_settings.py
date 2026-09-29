with open("sara/config/settings.py", "r") as f:
    content = f.read()

import re
if "disk_warning_percent" not in content:
    content = content.replace("class Settings(BaseSettings):", "class Settings(BaseSettings):\n    disk_warning_percent: float = 85.0\n    disk_critical_percent: float = 95.0")
    with open("sara/config/settings.py", "w") as f:
        f.write(content)
