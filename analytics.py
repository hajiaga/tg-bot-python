from parsers.database import ads_collection
from bson import ObjectId
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)

async def get_average_price_per_square_meter():
    """
    Возвращает среднюю цену за квадратный метр на основе объявлений в базе данных.
    """
    try:
        pipeline = [
            {"$match": {"price": {"$exists": True}, "title": {"$regex": r"\d+\s*m²"}}},
            {
                "$project": {
                    "price": {
                        "$convert": {
                            "input": {
                                "$trim": {
                                    "input": {
                                        "$replaceAll": {
                                            "input": "$price",
                                            "find": "AZN",
                                            "replacement": ""
                                        }
                                    }
                                }
                            },
                            "to": "double",
                            "onError": 0,
                            "onNull": 0
                        }
                    },
                    "square_meter": {
                        "$convert": {
                            "input": {"$arrayElemAt": [{"$split": ["$title", " m²"]}, 0]},
                            "to": "double",
                            "onError": 0,
                            "onNull": 0
                        }
                    },
                }
            },
            {
                "$match": {
                    "square_meter": {"$gt": 0}  # Фильтруем только те документы, у которых площадь больше 0
                }
            },
            {
                "$project": {
                    "price_per_square_meter": {"$divide": ["$price", "$square_meter"]}
                }
            },
            {"$group": {"_id": None, "avg_price_per_sqm": {"$avg": "$price_per_square_meter"}}},
        ]
        
        result = await ads_collection.aggregate(pipeline).to_list(1)
        logging.info(f"Pipeline result: {result}")
        return result[0]["avg_price_per_sqm"] if result else None
    except Exception as e:
        logging.error(f"Ошибка при расчете средней цены за квадратный метр: {e}")
        raise

async def get_price_dynamics(days=7):
    """
    Возвращает динамику роста/падения цен за последние n дней.
    """
    try:
        now = datetime.now()
        start_date = now - timedelta(days=days)
        
        pipeline = [
            {"$match": {"_id": {"$gte": ObjectId.from_datetime(start_date)}}},
            {"$group": {"_id": None, "average_price": {"$avg": "$price"}}},    
        ]
        
        result = await ads_collection.aggregate(pipeline).to_list(1)
        logging.info(f"Pipeline result: {result}")
        return result[0]["average_price"] if result else None
    except Exception as e:
        logging.error(f"Ошибка при расчете динамики цен: {e}")
        raise

async def analyze_data():
    """
    Функция для объединения анализа средней цены за квадратный метр и динамики цен.
    """
    try:
        avg_price_per_sqm = await get_average_price_per_square_meter()
        price_dynamics = await get_price_dynamics(days=7)
        
        return {
            "avg_price_per_sqm": avg_price_per_sqm,
            "price_dynamics": price_dynamics,
            "total_ads": await ads_collection.count_documents({})
        }
    except Exception as e:
        logging.error(f"Ошибка при анализе данных: {e}")
        raise