with open("app/main.py", "r") as f:
    content = f.read()

content = content.replace("await update.message.reply_html", "await (update.message or update.callback_query.message).reply_html")
content = content.replace("await update.message.reply_document", "await (update.message or update.callback_query.message).reply_document")
content = content.replace("await update.message.reply_markdown", "await (update.message or update.callback_query.message).reply_markdown")

with open("app/main.py", "w") as f:
    f.write(content)
