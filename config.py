import os

# Конфигурация базы данных
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = "bina_ads"
COLLECTION_NAME = "ads"

# Конфигурация Telegram бота
BOT_TOKEN = "1447044175:AAE3wgtczA7db1iG_L8ofODItACGjUnlpls"
CHAT_ID = "-4573303779"