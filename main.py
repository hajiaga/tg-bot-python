from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from parsers.bina_parser import parse_bina_ads
from parsers.database import save_ad_to_db, check_if_ad_exists

app = FastAPI()

# Создаем планировщик
scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def start_scheduler():
    scheduler.start()
    scheduler.add_job(fetch_and_save_new_ads, 'interval', minutes=10)

@app.on_event("shutdown")
async def shutdown_scheduler():
    scheduler.shutdown()

async def fetch_and_save_new_ads():
    ads = parse_bina_ads()
    for ad in ads:
        if not await check_if_ad_exists(ad):  # Используйте await для асинхронного вызова
            await save_ad_to_db(ad)           # Сохраняем новое объявление асинхронно
            await send_to_telegram(ad)        # Отправляем в Telegram

async def send_to_telegram(ad):
    from config import BOT_TOKEN, CHAT_ID
    from telegram import Bot
    bot = Bot(token=BOT_TOKEN)
    message = f"Новое объявление: {ad['title']}\nЦена: {ad['price']}\nСсылка: {ad['link']}"
    await bot.send_message(chat_id=CHAT_ID, text=message)cd 