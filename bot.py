import os
import hashlib
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
hashes = set()

def get_file_hash(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = None
    media_type = None

    if update.message.photo:
        file_id = update.message.photo[-1].file_id  # mayor resolución
        media_type = 'photo'
    elif update.message.video:
        file_id = update.message.video.file_id
        media_type = 'video'
    else:
        return  # no es foto ni video

    file = await context.bot.get_file(file_id)
    file_bytes = await file.download_as_bytearray()
    file_hash = get_file_hash(file_bytes)

    if file_hash in hashes:
        await update.message.delete()
        print(f"❌ {media_type} duplicado eliminado.")
    else:
        hashes.add(file_hash)
        print(f"✅ {media_type} registrado.")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))
    print("✅ Bot corriendo...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
