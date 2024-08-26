import asyncio
from telegram import Bot

# Ваш токен бота и ID чата
BOT_TOKEN = "1447044175:AAEbx-WaYvf-YctPeamnaBJ8Kv4AktvNVIo"
CHAT_ID = "-4573303779"

# Создаем объект бота
bot = Bot(token=BOT_TOKEN)

async def send_message_periodically():
    while True:
        await bot.send_message(chat_id=CHAT_ID, text="Привет")
        await asyncio.sleep(1)  # Ожидаем 1 секунду

if __name__ == "__main__":
    asyncio.run(send_message_periodically())