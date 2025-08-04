import os
import hashlib
from flask import Flask, request
from telegram import Update, MessageEntity
from telegram.ext import Application, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")
APP_URL = os.getenv("APP_URL")  # eg: https://tu-bot.onrender.com

# Almacenamos hashes para evitar duplicados
known_hashes = set()

app = Flask(__name__)

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    file = None

    # Detecta si es foto
    if message.photo:
        file = message.photo[-1]
    elif message.video:
        file = message.video
    else:
        return

    file_id = file.file_unique_id  # Único por contenido
    if file_id in known_hashes:
        try:
            await message.delete()
            print(f"Contenido duplicado eliminado.")
        except Exception as e:
            print(f"No se pudo eliminar el mensaje: {e}")
    else:
        known_hashes.add(file_id)
        print(f"Contenido nuevo guardado: {file_id}")

# Inicializa el bot de telegram
telegram_app = Application.builder().token(TOKEN).build()
telegram_app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))

@app.route(f"/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), telegram_app.bot)
        telegram_app.update_queue.put(update)
        return "ok"

@app.route("/")
def index():
    return "Bot activo"

async def set_webhook():
    webhook_url = f"{APP_URL}/webhook"
    await telegram_app.bot.set_webhook(url=webhook_url)
    print(f"Webhook configurado en {webhook_url}")

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_webhook())
    telegram_app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        webhook_url=f"{APP_URL}/webhook"
    )


if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    web_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

