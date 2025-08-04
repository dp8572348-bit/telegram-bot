from flask import Flask, request
import os
from bot import get_app

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
app = Flask(__name__)
telegram_app = get_app()

@app.route("/")
def index():
    return "Bot activo con Webhook", 200

@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = telegram_app.update_queue._loop.run_until_complete(
        telegram_app.bot.initialize()
    )
    telegram_app.update_queue.put_nowait(request.get_json(force=True))
    return "OK", 200

if __name__ == "__main__":
    telegram_app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        webhook_url=os.getenv("WEBHOOK_URL") + WEBHOOK_PATH
    )
