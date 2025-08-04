from fastapi import FastAPI, Request
from telegram import Update
from bot import main as telegram_bot
import asyncio

fastapi_app = FastAPI()

@fastapi_app.post(f"/webhook/{telegram_bot.BOT_TOKEN}")
async def webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, telegram_bot.app.bot)
    await telegram_bot.app.process_update(update)
    return {"ok": True}

@fastapi_app.on_event("startup")
async def startup():
    webhook_url = f"https://TU_SERVICIO.onrender.com/webhook/{telegram_bot.BOT_TOKEN}"
    await telegram_bot.app.bot.set_webhook(webhook_url)
