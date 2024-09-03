from parsers.database import ads_collection
from datetime import datetime, timedelta
import re

async def get_average_price_per_square_meter():
    """
    Возвращает среднюю цену за квадратный метр на основе объявлений в базе данных.
    """
    pipeline = [
        {"$match": {"price": {"$exists": True}, "title": {"$regex": r"\d+\s*m²"}}},
        {
            "$project": {
                "price": 1,
                "square_meter": {
                    # Извлечение числового значения из строки
                    "$toDouble": {
                        "$arrayElemAt": [
                            {"$split": [{"$arrayElemAt": [{"$split": ["$title", ", "]}, 1]}, " m²"]}, 0
                        ]
                    }
                },
            }
        },
        {"$project": {"price_per_square_meter": {"$divide": ["$price", "$square_meter"]}}},
        {"$group": {"_id": None, "avg_price_per_sqm": {"$avg": "$price_per_square_meter"}}},
    ]
    
    result = await ads_collection.aggregate(pipeline).to_list(1)
    return result[0]["avg_price_per_sqm"] if result else None

async def get_price_dynamics(days=7):
    """
    Возвращает динамику роста/падения цен за последние n дней.
    """
    now = datetime.now()
    start_date = now - timedelta(days=days)
    
    pipeline = [
        {"$match": {"_id": {"$gte": ObjectId.from_datetime(start_date)}}},
        {"$group": {"_id": None, "average_price": {"$avg": "$price"}}},    
    ]
    
    result = await ads_collection.aggregate(pipeline).to_list(1)
    return result[0]["average_price"] if result else None

async def analyze_data():
    """
    Выполняет анализ данных и возвращает результаты.
    """
    total_ads = await ads_collection.count_documents({})
    avg_price_per_sqm = await get_average_price_per_square_meter()
    
    return {
        "total_ads": total_ads,
        "avg_price_per_sqm": avg_price_per_sqm,
    }