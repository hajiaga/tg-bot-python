import os

# Конфигурация базы данных
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = "bina_ads"
COLLECTION_NAME = "ads"

# Конфигурация Telegram бота
BOT_TOKEN = "1447044175:AAEbx-WaYvf-YctPeamnaBJ8Kv4AktvNVIo"
CHAT_ID = "-4573303779"