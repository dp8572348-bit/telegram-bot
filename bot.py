import os
import json
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

# Cargar .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
HASHES_FILE = "hashes.json"

# Cargar hashes previos
try:
    with open(HASHES_FILE, "r") as f:
        hashes = json.load(f)
except FileNotFoundError:
    hashes = {}

# Manejador de fotos y videos
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat_id = str(message.chat_id)
    user = message.from_user

    if not message.chat.type in ["group", "supergroup"]:
        return

    file_unique_id = None
    if message.photo:
        file_unique_id = message.photo[-1].file_unique_id
    elif message.video:
        file_unique_id = message.video.file_unique_id
    else:
        return

    if chat_id not in hashes:
        hashes[chat_id] = []

    if file_unique_id in hashes[chat_id]:
        try:
            await message.delete()
            print(f"🗑️ Mensaje repetido eliminado de @{user.username}")
        except Exception as e:
            print(f"⚠️ No se pudo eliminar mensaje: {e}")
    else:
        hashes[chat_id].append(file_unique_id)
        with open(HASHES_FILE, "w") as f:
            json.dump(hashes, f)

# EJECUCIÓN DIRECTA (sin asyncio.run)
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))
    print("✅ Bot corriendo...")
    app.run_polling()  # NO uses asyncio.run() aquí

if __name__ == "__main__":
    main()

