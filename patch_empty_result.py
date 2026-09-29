import re

with open("app/main.py", "r") as f:
    content = f.read()

bad = """                                    if result_str:
                                        short_res = result_str if len(result_str) < 800 else result_str[:800] + "...(truncated)"
                                        fin_text += f"📝 <b>Result</b>\\n<pre>{short_res}</pre>\\n\\n"
"""

good = """                                    if result_str:
                                        short_res = result_str if len(result_str) < 800 else result_str[:800] + "...(truncated)"
                                        fin_text += f"📝 <b>Result</b>\\n<pre>{short_res}</pre>\\n\\n"
                                    else:
                                        fin_text += f"⚠️ <b>No readable final agent summary was returned.</b>\\nFull execution log is available.\\n\\n"
"""

content = content.replace(bad, good)

with open("app/main.py", "w") as f:
    f.write(content)
