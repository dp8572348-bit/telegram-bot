import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

HASHES_FILE = "hashes.json"

# Cargar hashes guardados (file_unique_id por chat)
if os.path.exists(HASHES_FILE):
    with open(HASHES_FILE, "r") as f:
        hashes = json.load(f)
else:
    hashes = {}

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat_id = message.chat_id
    user = message.from_user

    # Solo en grupos o supergrupos
    if not message.chat.type in ["group", "supergroup"]:
        return

    file_unique_id = None
    if message.photo:
        file_unique_id = message.photo[-1].file_unique_id  # Foto tamaño más grande
    elif message.video:
        file_unique_id = message.video.file_unique_id
    else:
        return

    chat_hashes = hashes.get(str(chat_id), [])

    if file_unique_id in chat_hashes:
        try:
            await message.delete()
            print(f"Mensaje de @{user.username if user.username else user.id} eliminado por archivo repetido")
        except Exception as e:
            print(f"No se pudo eliminar mensaje: {e}")
    else:
        chat_hashes.append(file_unique_id)
        hashes[str(chat_id)] = chat_hashes
        # Guardar hashes a disco
        with open(HASHES_FILE, "w") as f:
            json.dump(hashes, f)

if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("ERROR: Debes definir BOT_TOKEN en .env")
        exit(1)

    app = ApplicationBuilder().token(TOKEN).build()

    media_filter = filters.PHOTO | filters.VIDEO
    app.add_handler(MessageHandler(media_filter, handle_media))

    print("Bot iniciado...")
    app.run_polling()


    print("Bot iniciado...")
    app.run_polling()
