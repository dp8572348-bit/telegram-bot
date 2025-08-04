from telegram import Update, Message
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import os
import hashlib

# Diccionario para almacenar hashes de medios por chat
media_hashes = {}

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message: Message = update.message
    chat_id = message.chat_id

    # Obtener el archivo
    file = None
    if message.photo:
        file = await message.photo[-1].get_file()
    elif message.video:
        file = await message.video.get_file()
    else:
        return  # Ignorar si no es imagen o video

    # Descargar el archivo en bytes
    file_bytes = await file.download_as_bytearray()
    media_hash = hashlib.sha256(file_bytes).hexdigest()

    if chat_id not in media_hashes:
        media_hashes[chat_id] = set()

    if media_hash in media_hashes[chat_id]:
        await message.delete()
        print(f"Archivo duplicado eliminado en chat {chat_id}")
    else:
        media_hashes[chat_id].add(media_hash)
        print(f"Nuevo archivo registrado en chat {chat_id}")

def get_app():
    token = os.getenv("BOT_TOKEN")
    app = Application.builder().token(token).build()
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))
    return app



if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    web_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

