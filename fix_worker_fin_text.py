with open("app/main.py", "r") as f:
    content = f.read()

bad_block = """                                    if result_str:
                                        short_res = result_str if len(result_str) < 800 else result_str[:800] + "...(truncated)"
                                        fin_text += f"📝 <b>Result</b>\\n<pre>{short_res}</pre>\\n\\n"

                                        f"Duration: {dur_str}\\n"
                                        f"Exit code: {exit_code}\\n"
                                        f"Log: <code>{log_file_path.name}</code>"
                                    )"""

good_block = """                                    if result_str:
                                        short_res = result_str if len(result_str) < 800 else result_str[:800] + "...(truncated)"
                                        fin_text += f"📝 <b>Result</b>\\n<pre>{short_res}</pre>\\n\\n"
"""

content = content.replace(bad_block, good_block)

with open("app/main.py", "w") as f:
    f.write(content)
