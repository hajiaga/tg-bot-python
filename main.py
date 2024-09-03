import logging
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from parsers.bina_parser import parse_bina_ads
from parsers.database import save_ad_to_db, check_if_ad_exists, ads_collection
from analytics import get_average_price_per_square_meter, get_price_dynamics
from datetime import datetime, timedelta
from bson import ObjectId

app = FastAPI()

templates = Jinja2Templates(directory="templates")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def start_scheduler():
    scheduler.start()
    scheduler.add_job(fetch_and_save_new_ads, 'interval', minutes=10)
    scheduler.add_job(send_daily_report, 'interval', minutes=2)  # For testing purposes

@app.on_event("shutdown")
async def shutdown_scheduler():
    scheduler.shutdown()

async def fetch_and_save_new_ads():
    ads = parse_bina_ads()
    for ad in ads:
        if not await check_if_ad_exists(ad):
            await save_ad_to_db(ad)
            await send_to_telegram(ad)

async def send_to_telegram(ad):
    from config import BOT_TOKEN, CHAT_ID
    from telegram import Bot
    bot = Bot(token=BOT_TOKEN)
    message = f"New listing: {ad['title']}\nPrice: {ad['price']}\nLink: {ad['link']}"
    await bot.send_message(chat_id=CHAT_ID, text=message)

async def send_daily_report():
    from config import BOT_TOKEN, CHAT_ID
    from telegram import Bot
    bot = Bot(token=BOT_TOKEN)

    logger.info("Sending daily report")

    try:
        avg_price_per_sqm = await get_average_price_per_square_meter()
        price_dynamics = await get_price_dynamics()

        if avg_price_per_sqm or price_dynamics:
            message = (
                f"Daily Report:\n"
                f"Total Listings: {await ads_collection.count_documents({})}\n"
                f"Average Price per SqM: {avg_price_per_sqm:.2f} AZN\n"
                f"Price Dynamics (7 days): {price_dynamics:.2f} AZN"
            )
        else:
            message = "Analysis returned no results"

        await bot.send_message(chat_id=CHAT_ID, text=message)
        logger.info("Report sent successfully")
    except Exception as e:
        error_msg = f"Error sending report: {e}"
        await bot.send_message(chat_id=CHAT_ID, text=error_msg)
        logger.error(error_msg)

@app.get("/")
async def read_root(request: Request):
    now = datetime.now()
    last_24_hours = now - timedelta(hours=24)
    
    ads_in_last_24_hours = await ads_collection.count_documents({
        "_id": {"$gte": ObjectId.from_datetime(last_24_hours)}
    })
    
    return templates.TemplateResponse("index.html", {"request": request, "ads_last_24_hours": ads_in_last_24_hours})