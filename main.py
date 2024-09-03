import logging
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from parsers.bina_parser import parse_bina_ads
from parsers.database import save_ad_to_db, check_if_ad_exists, ads_collection
from analytics import analyze_data  # Импорт аналитического модуля
from datetime import datetime, timedelta
from bson import ObjectId

# Initialize FastAPI app
app = FastAPI()

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create scheduler
scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def start_scheduler():
    scheduler.start()
    scheduler.add_job(fetch_and_save_new_ads, 'interval', minutes=10)
    scheduler.add_job(send_daily_report, 'interval', minutes=2)  # Run the report every 2 minutes for testing

@app.on_event("shutdown")
async def shutdown_scheduler():
    scheduler.shutdown()

async def fetch_and_save_new_ads():
    ads = parse_bina_ads()
    for ad in ads:
        if not await check_if_ad_exists(ad):  # Use await for asynchronous call
            await save_ad_to_db(ad)           # Save the new ad asynchronously
            await send_to_telegram(ad)        # Send to Telegram

async def send_to_telegram(ad):
    from config import BOT_TOKEN, CHAT_ID
    from telegram import Bot
    bot = Bot(token=BOT_TOKEN)
    message = f"New Ad: {ad['title']}\nPrice: {ad['price']}\nLink: {ad['link']}"
    await bot.send_message(chat_id=CHAT_ID, text=message)

# Send daily report with logging
async def send_daily_report():
    from config import BOT_TOKEN, CHAT_ID
    from telegram import Bot
    bot = Bot(token=BOT_TOKEN)

    logger.info("Starting to send the daily report")

    try:
        analysis = await analyze_data()
        logger.info(f"Analysis result: {analysis}")

        if analysis:
            avg_price_per_sqm = analysis.get('avg_price_per_sqm')
            total_ads = analysis.get('total_ads')
            price_dynamics = analysis.get('price_dynamics')

            if avg_price_per_sqm is not None:
                message = (
                    f"Daily Report:\n"
                    f"Total Ads: {total_ads}\n"
                    f"Avg Price per Sqm: {avg_price_per_sqm:.2f} AZN"
                )
            else:
                message = (
                    f"Daily Report:\n"
                    f"Total Ads: {total_ads}\n"
                    f"Avg Price per Sqm: No data"
                )

            if price_dynamics is not None:
                message += f"\nPrice Dynamics over last 7 days: {price_dynamics:.2f} AZN"
            else:
                message += f"\nPrice Dynamics over last 7 days: No data"

            await bot.send_message(chat_id=CHAT_ID, text=message)
            logger.info("Report sent successfully")
        else:
            warning_msg = "Analysis returned no results"
            await bot.send_message(chat_id=CHAT_ID, text=warning_msg)
            logger.warning(warning_msg)
    except Exception as e:
        error_msg = f"Error sending report: {e}"
        await bot.send_message(chat_id=CHAT_ID, text=error_msg)
        logger.error(error_msg)

# Route for the home page
@app.get("/")
async def read_root(request: Request):
    # Get current time and calculate time 24 hours ago
    now = datetime.now()
    last_24_hours = now - timedelta(hours=24)
    
    # MongoDB query to count ads in the last 24 hours
    ads_in_last_24_hours = await ads_collection.count_documents({
        "_id": {"$gte": ObjectId.from_datetime(last_24_hours)}
    })
    
    return templates.TemplateResponse("index.html", {"request": request, "ads_last_24_hours": ads_in_last_24_hours})