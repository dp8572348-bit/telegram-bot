import hashlib
from io import BytesIO
from PIL import Image
from telegram import Update, Message
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Token del bot
BOT_TOKEN = "7594947845:AAF56XDXBWl1vt01CW_vl5FI5VfIhrUmjQI"

# Hashes guardados
hashes = set()

app = ApplicationBuilder().token(BOT_TOKEN).build()

def get_file_hash(file_bytes: bytes) -> str:
    return hashlib.md5(file_bytes).hexdigest()

async def eliminar_duplicados(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message: Message = update.message
    file = None

    if message.photo:
        file = await context.bot.get_file(message.photo[-1].file_id)
    elif message.video:
        file = await context.bot.get_file(message.video.file_id)
    else:
        return  # Ignora otros mensajes

    file_bytes = await file.download_as_bytearray()
    hash_actual = get_file_hash(file_bytes)

    if hash_actual in hashes:
        await message.delete()
        print("Mensaje duplicado eliminado")
    else:
        hashes.add(hash_actual)
        print("Mensaje nuevo guardado")

app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, eliminar_duplicados))
