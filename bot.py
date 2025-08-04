import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")
APP_URL = os.getenv("APP_URL")  # Ej: https://tu-app.onrender.com

app = Flask(__name__)
known_hashes = set()

# Manejar fotos y videos
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
            print("Mensaje duplicado eliminado.")
        except Exception as e:
            print(f"Error al eliminar: {e}")
    else:
        known_hashes.add(file_id)
        print(f"Contenido nuevo registrado: {file_id}")

telegram_app = Application.builder().token(TOKEN).build()
telegram_app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))

# Webhook para recibir updates
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    asyncio.run_coroutine_threadsafe(telegram_app.update_queue.put(update), telegram_app.loop)
    return "ok"

@app.route("/")
def index():
    return "Bot activo."

# Configurar webhook en Telegram
async def main():
    await telegram_app.bot.set_webhook(f"{APP_URL}/webhook")
    print(f"Webhook configurado en {APP_URL}/webhook")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    asyncio.run(main())
    app.run(host="0.0.0.0", port=port)

