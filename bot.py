import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters
import asyncio

TOKEN = os.getenv("BOT_TOKEN")
APP_URL = os.getenv("APP_URL")  # ej: https://telegram-bot-tuapp.onrender.com

app = Flask(__name__)

known_hashes = set()

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    file = None

    if message.photo:
        file = message.photo[-1]
    elif message.video:
        file = message.video
    else:
        return

    file_id = file.file_unique_id
    if file_id in known_hashes:
        try:
            await message.delete()
            print("Mensaje duplicado eliminado")
        except Exception as e:
            print(f"No se pudo eliminar mensaje: {e}")
    else:
        known_hashes.add(file_id)
        print(f"Contenido nuevo guardado: {file_id}")

telegram_app = Application.builder().token(TOKEN).build()
telegram_app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    asyncio.run_coroutine_threadsafe(telegram_app.update_queue.put(update), telegram_app.loop)
    return "ok"

@app.route("/")
def index():
    return "Bot activo"

async def set_webhook():
    webhook_url = f"{APP_URL}/webhook"
    await telegram_app.bot.set_webhook(url=webhook_url)
    print(f"Webhook configurado en {webhook_url}")

if __name__ == "__main__":
    import sys
    port = int(os.environ.get("PORT", 5000))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_webhook())
    telegram_app.create_task(telegram_app.initialize())  # Inicializar correctamente la app
    telegram_app.create_task(telegram_app.start())
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    web_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

