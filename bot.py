import os
from telegram import Update, Message
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
from hashlib import md5

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Diccionario para almacenar hashes
hashes = set()

async def eliminar_repetidos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje: Message = update.message
    if not mensaje or not mensaje.chat or not mensaje.from_user:
        return

    # Obtener el archivo
    archivo = None
    if mensaje.photo:
        archivo = await mensaje.photo[-1].get_file()
    elif mensaje.video:
        archivo = await mensaje.video.get_file()
    else:
        return

    # Descargar el archivo como bytes
    contenido = await archivo.download_as_bytearray()

    # Calcular hash md5
    archivo_hash = md5(contenido).hexdigest()

    if archivo_hash in hashes:
        await mensaje.delete()
        print(f"Archivo repetido eliminado en el grupo {mensaje.chat.id}")
    else:
        hashes.add(archivo_hash)

if __name__ == "__main__":
    print("✅ Bot iniciado. Escuchando mensajes...")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, eliminar_repetidos))
    
    # No uses asyncio.run(main()) aquí
    app.run_polling()
