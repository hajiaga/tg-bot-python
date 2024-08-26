from motor.motor_asyncio import AsyncIOMotorClient

# Подключение к MongoDB
MONGO_DETAILS = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_DETAILS)

database = client['ads_database']  # Название вашей базы данных
ads_collection = database['ads_collection']  # Название вашей коллекции

async def save_ad_to_db(ad):
    await ads_collection.insert_one(ad)

async def check_if_ad_exists(ad):
    existing_ad = await ads_collection.find_one({"link": ad["link"]})
    return existing_ad is not None