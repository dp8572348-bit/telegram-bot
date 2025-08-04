import os
import hashlib
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

HASHES_FILE = "hashes.json"

# Cargar hashes desde archivo
if os.path.exists(HASHES_FILE):
    with open(HASHES_FILE, "r") as f:
        hashes = json.load(f)
else:
    hashes = {}

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat_id = message.chat_id
    user = message.from_user

    # Solo grupos
    if not message.chat.type in ["group", "supergroup"]:
        return

    file_id = None
    if message.photo:
        # photo viene como lista de tamaños, tomamos la más grande
        file_id = message.photo[-1].file_id
    elif message.video:
        file_id = message.video.file_id
    else:
        return

    # Descargar archivo
    file = await context.bot.get_file(file_id)
    file_path = f"temp_{file_id}"
    await file.download_to_drive(file_path)

    # Calcular hash SHA256
    with open(file_path, "rb") as f:
        file_bytes = f.read()
        file_hash = hashlib.sha256(file_bytes).hexdigest()

    os.remove(file_path)

    # Verificar si hash ya existe para este chat
    chat_hashes = hashes.get(str(chat_id), [])

    if file_hash in chat_hashes:
        # Archivo repetido: eliminar mensaje
        try:
            await message.delete()
            print(f"Mensaje de {user.username} eliminado por archivo repetido")
        except Exception as e:
            print(f"No se pudo eliminar mensaje: {e}")
    else:
        # Guardar nuevo hash
        chat_hashes.append(file_hash)
        hashes[str(chat_id)] = chat_hashes
        with open(HASHES_FILE, "w") as f:
            json.dump(hashes, f)


if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv

    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")

    app = ApplicationBuilder().token(TOKEN).build()

    media_filter = filters.PHOTO | filters.VIDEO

    app.add_handler(MessageHandler(media_filter, handle_media))

    print("Bot iniciado...")
    app.run_polling()
