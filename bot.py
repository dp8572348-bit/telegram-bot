import os
import hashlib
from flask import Flask, request, abort
from telegram import Bot, Update
from telegram.ext import Dispatcher, MessageHandler, filters

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN no está definido en variables de entorno")

bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

hashes = set()

def get_file_hash(file_path):
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def handle_media(update, context):
    message = update.message
    if not message:
        return

    file_id = None
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.video:
        file_id = message.video.file_id

    if file_id:
        file = bot.get_file(file_id)
        file_path = f"{file_id}.tmp"
        file.download(file_path)

        media_hash = get_file_hash(file_path)
        os.remove(file_path)

        if media_hash in hashes:
            message.delete()
        else:
            hashes.add(media_hash)

handler = MessageHandler(filters.PHOTO | filters.VIDEO, handle_media)
dispatcher.add_handler(handler)

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
        return "ok"
    else:
        abort(403)

@app.route("/")
def index():
    return "Bot is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    web_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

