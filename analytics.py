from parsers.database import ads_collection
from datetime import datetime, timedelta
from bson import ObjectId

async def analyze_data():
    """
    Выполняет анализ данных и возвращает результат в виде словаря.
    """
    total_ads = await ads_collection.count_documents({})
    avg_price_per_sqm = await get_average_price_per_square_meter()

    return {
        "total_ads": total_ads,
        "avg_price_per_sqm": avg_price_per_sqm
    }

async def get_average_price_per_square_meter():
    """
    Возвращает среднюю цену за квадратный метр на основе объявлений в базе данных.
    """
    pipeline = [
        {"$match": {"price": {"$exists": True}, "title": {"$regex": r"\d+\s*m²"}}},
        {
            "$project": {
                "price": {
                    "$toDouble": {
                        "$replaceAll": {"input": {"$replaceAll": {"input": "$price", "find": " AZN", "replacement": ""}}, "find": " ", "replacement": ""}
                    }
                },
                "square_meter": {
                    "$toDouble": {"$arrayElemAt": [{"$split": ["$title", " m²"]}, -2]}
                },
            }
        },
        {"$project": {"price_per_square_meter": {"$divide": ["$price", "$square_meter"]}}},
        {"$group": {"_id": None, "avg_price_per_sqm": {"$avg": "$price_per_square_meter"}}},
    ]
    
    result = await ads_collection.aggregate(pipeline).to_list(1)
    return result[0]["avg_price_per_sqm"] if result else None