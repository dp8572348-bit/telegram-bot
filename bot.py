import os
import json
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
from aiohttp import web

HASHES_FILE = "hashes.json"

if os.path.exists(HASHES_FILE):
    with open(HASHES_FILE, "r") as f:
        hashes = json.load(f)
else:
    hashes = {}

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat_id = message.chat_id
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
        with open(HASHES_FILE, "w") as f:
            json.dump(hashes, f)

async def run_bot():
    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("ERROR: BOT_TOKEN no definido en .env")
        exit(1)

    app = ApplicationBuilder().token(TOKEN).build()
    media_filter = filters.PHOTO | filters.VIDEO
    app.add_handler(MessageHandler(media_filter, handle_media))

    print("Bot iniciado...")
    await app.run_polling()

# Servidor web simple para mantener vivo el proceso en Render
async def handle(request):
    return web.Response(text="Bot funcionando")

def start_webserver():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    port = int(os.environ.get("PORT", 10000))
    web.run_app(app, port=port)

if __name__ == "__main__":
    # Ejecutar bot y servidor web simultáneamente
    loop = asyncio.get_event_loop()
    # Crear tarea para el bot
    bot_task = loop.create_task(run_bot())
    # Crear tarea para servidor web en hilo aparte
    from threading import Thread
    server_thread = Thread(target=start_webserver, daemon=True)
    server_thread.start()
    # Ejecutar loop principal con el bot
    loop.run_until_complete(bot_task)



    print("Bot iniciado...")
    app.run_polling()
