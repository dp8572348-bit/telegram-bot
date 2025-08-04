import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

HASHES_FILE = "hashes.json"

# Cargar hashes desde disco
if os.path.exists(HASHES_FILE):
    with open(HASHES_FILE, "r") as f:
        hashes = json.load(f)
else:
    hashes = {}

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat_id = str(message.chat_id)
    user = message.from_user

    # Solo grupos
    if message.chat.type not in ["group", "supergroup"]:
        return

    file_unique_id = None
    if message.photo:
        file_unique_id = message.photo[-1].file_unique_id
    elif message.video:
        file_unique_id = message.video.file_unique_id
    else:
        return

    chat_hashes = hashes.get(chat_id, [])

    if file_unique_id in chat_hashes:
        try:
            await message.delete()
            print(f"Eliminado mensaje de @{user.username or user.id} por duplicado.")
        except Exception as e:
            print(f"No se pudo eliminar el mensaje: {e}")
    else:
        chat_hashes.append(file_unique_id)
        hashes[chat_id] = chat_hashes
        with open(HASHES_FILE, "w") as f:
            json.dump(hashes, f)

async def main():
    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("❌ BOT_TOKEN no definido en .env")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    media_filter = filters.PHOTO | filters.VIDEO
    app.add_handler(MessageHandler(media_filter, handle_media))

    print("✅ Bot iniciado. Escuchando mensajes...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
