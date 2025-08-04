import os
import json
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes,
)

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
HASHES_FILE = "hashes.json"

# Cargar hashes guardados (si existen)
try:
    with open(HASHES_FILE, "r") as f:
        hashes = json.load(f)
except FileNotFoundError:
    hashes = {}

# Manejador para fotos y videos
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
            print(f"📛 Mensaje de @{user.username} eliminado (repetido)")
        except Exception as e:
            print(f"⚠️ No se pudo eliminar el mensaje: {e}")
    else:
        hashes[chat_id].append(file_unique_id)
        with open(HASHES_FILE, "w") as f:
            json.dump(hashes, f)

async def start_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))
    print("✅ Bot corriendo...")
    await app.run_polling()  # ¡NO se encierra dentro de asyncio.run ni loops manuales!

if __name__ == "__main__":
    import asyncio
    asyncio.run(start_bot())
