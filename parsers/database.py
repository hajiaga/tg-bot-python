from motor.motor_asyncio import AsyncIOMotorClient

# Подключение к MongoDB
MONGO_DETAILS = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_DETAILS)

database = client['ads_database']  # Название вашей базы данных
ads_collection = database['ads_collection']  # Название вашей коллекции

async def save_ad_to_db(ad):
    # Извлекаем площадь из заголовка объявления, например "1 otaqlı, 68.3 m²"
    try:
        size_in_sqm = float(ad['title'].split(',')[-1].replace('m²', '').strip())
        price = float(ad['price'].replace('AZN', '').replace(' ', '').strip())
        price_per_sqm = price / size_in_sqm
    except (ValueError, IndexError) as e:
        # Если не удалось распарсить данные, пропускаем расчет цены за квадратный метр
        price_per_sqm = None

    ad_data = {
        "title": ad['title'],
        "price": ad['price'],
        "location": ad['location'],
        "link": ad['link'],
        "price_per_sqm": price_per_sqm  # Сохраняем цену за квадратный метр
    }

    await ads_collection.insert_one(ad_data)

async def check_if_ad_exists(ad):
    existing_ad = await ads_collection.find_one({"link": ad["link"]})
    return existing_ad is not None