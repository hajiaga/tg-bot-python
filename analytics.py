from parsers.database import ads_collection
from datetime import datetime, timedelta

async def analyze_data():
    # Получаем текущую дату
    now = datetime.now()
    one_day_ago = now - timedelta(days=1)
    
    # Запрос всех объявлений за последние 24 часа
    recent_ads = await ads_collection.find({
        "_id": {"$gte": ObjectId.from_datetime(one_day_ago)}
    }).to_list(length=None)

    total_price = 0
    total_area = 0
    total_ads = len(recent_ads)

    for ad in recent_ads:
        # Извлечение площади и цены
        try:
            area = float(ad['title'].split(',')[1].strip().split()[0])
            price = float(ad['price'].split()[0].replace(",", ""))
            total_price += price
            total_area += area
        except (ValueError, IndexError):
            continue

    if total_area > 0:
        avg_price_per_sqm = total_price / total_area
    else:
        avg_price_per_sqm = 0

    return {
        "total_ads": total_ads,
        "avg_price_per_sqm": avg_price_per_sqm
    }