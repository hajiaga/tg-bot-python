import asyncio
from telegram import Bot
from config import BOT_TOKEN, CHAT_ID

async def send_test_message():
    bot = Bot(token=BOT_TOKEN)
    
    ad = {
        "title": "1 otaqlı, 65.1 m², 17/20 mərtəbə",
        "price": "198 500 AZN",
        "location": "Şah İsmayıl Xətai m.",
        "link": "https://bina.az/items/4567500"
    }

    message = f"Новое объявление:\n{ad['title']}\nЦена: {ad['price']}\nЛокация: {ad['location']}\nСсылка: {ad['link']}"
    await bot.send_message(chat_id=CHAT_ID, text=message)

# Запуск асинхронной функции
asyncio.run(send_test_message())