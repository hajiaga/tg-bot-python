import logging
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from parsers.bina_parser import parse_bina_ads
from parsers.database import save_ad_to_db, check_if_ad_exists, ads_collection
from analytics import analyze_data  # Импорт аналитического модуля
from datetime import datetime, timedelta
from bson import ObjectId

app = FastAPI()

# Подключение Jinja2
templates = Jinja2Templates(directory="templates")

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем планировщик
scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def start_scheduler():
    scheduler.start()
    scheduler.add_job(fetch_and_save_new_ads, 'interval', minutes=10)
    scheduler.add_job(send_daily_report, 'interval', minutes=2)  # Запускаем отчет каждые 2 минуты для тестирования

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
    await bot.send_message(chat_id=CHAT_ID, text=message)

# Отправка ежедневного отчета с логированием
async def send_daily_report():
    from config import BOT_TOKEN, CHAT_ID
    from telegram import Bot
    bot = Bot(token=BOT_TOKEN)

    logger.info("Запуск отправки ежедневного отчета")

    try:
        analysis = await analyze_data()
        logger.info(f"Результат анализа: {analysis}")

        if analysis:
            message = (f"Ежедневный отчет:\n"
                       f"Всего объявлений: {analysis['total_ads']}\n"
                       f"Средняя цена за квадратный метр: {analysis['avg_price_per_sqm']:.2f} AZN")
            await bot.send_message(chat_id=CHAT_ID, text=message)
            logger.info("Отчет успешно отправлен")
        else:
            warning_msg = "Анализ не дал результатов"
            await bot.send_message(chat_id=CHAT_ID, text=warning_msg)
            logger.warning(warning_msg)
    except Exception as e:
        error_msg = f"Ошибка при отправке отчета: {e}"
        await bot.send_message(chat_id=CHAT_ID, text=error_msg)
        logger.error(error_msg)

# Маршрут для главной страницы
@app.get("/")
async def read_root(request: Request):
    # Получаем текущее время и рассчитываем время 24 часа назад
    now = datetime.now()
    last_24_hours = now - timedelta(hours=24)
    
    # Запрос к MongoDB для подсчета объявлений за последние 24 часа
    ads_in_last_24_hours = await ads_collection.count_documents({
        "_id": {"$gte": ObjectId.from_datetime(last_24_hours)}
    })
    
    return templates.TemplateResponse("index.html", {"request": request, "ads_last_24_hours": ads_in_last_24_hours})