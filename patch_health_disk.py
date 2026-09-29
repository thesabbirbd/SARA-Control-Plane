with open("app/main.py", "r") as f:
    content = f.read()

import re

old_disk = 'disk_warning = " ⚠️" if disk >= 85 else ""'
new_disk = 'disk_warning = " 🚨 CRITICAL" if disk >= settings.disk_critical_percent else " ⚠️" if disk >= settings.disk_warning_percent else ""'

content = content.replace(old_disk, new_disk)
with open("app/main.py", "w") as f:
    f.write(content)
