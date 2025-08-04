import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from collections import defaultdict
import asyncio
import hashlib

# Obtener el token del bot de las variables de entorno
TOKEN = os.getenv("BOT_TOKEN")  # Asegúrate de configurarlo en Render

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Estructura para guardar hashes de archivos por grupo
file_hashes_by_chat = defaultdict(set)

# Función para calcular hash MD5 de un archivo binario
async def calculate_hash(file):
    data = await file.download_as_bytearray()
    return hashlib.md5(data).hexdigest()

# Manejador de mensajes multimedia (fotos y videos)
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    file = None

    if message.photo:
        file = await message.photo[-1].get_file()
    elif message.video:
        file = await message.video.get_file()
    else:
        return

    file_hash = await calculate_hash(file)
    chat_id = message.chat_id

    if file_hash in file_hashes_by_chat[chat_id]:
        logger.info(f"Archivo duplicado en {chat_id}, eliminando mensaje...")
        await message.delete()
    else:
        logger.info(f"Nuevo archivo en {chat_id}, guardando hash.")
        file_hashes_by_chat[chat_id].add(file_hash)

# Función principal
async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))
    print("✅ Bot corriendo...")

    await app.run_polling()

# Manejo del loop para entornos como Render
if __name__ == '__main__':
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())

