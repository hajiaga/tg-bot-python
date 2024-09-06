import logging
from parsers.database import ads_collection
from bson import ObjectId
from datetime import datetime, timedelta

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
                        "$toDouble": {
                            "$replaceAll": {
                                "input": {"$trim": {"input": "$price", "chars": " AZN"}},
                                "find": " ",
                                "replacement": ""
                            }
                        }
                    },
                    "square_meter": {
                        "$convert": {
                            "input": {"$arrayElemAt": [{"$split": ["$title", " m²"]}, 0]},
                            "to": "double",
                            "onError": 0,
                            "onNull": 0
                        }
                    }
                }
            },
            {
                "$project": {
                    "price_per_square_meter": {
                        "$cond": {
                            "if": {"$eq": ["$square_meter", 0]},
                            "then": None,  # Avoid division by zero
                            "else": {"$divide": ["$price", "$square_meter"]}
                        }
                    }
                }
            },
            {"$match": {"price_per_square_meter": {"$ne": None}}},  # Exclude invalid values
            {"$group": {"_id": None, "avg_price_per_sqm": {"$avg": "$price_per_square_meter"}}},
        ]

        result = await ads_collection.aggregate(pipeline).to_list(1)
        logging.info(f"Pipeline result: {result}")
        return result[0]["avg_price_per_sqm"] if result else None
    except Exception as e:
        logging.error(f"Ошибка при расчете средней цены за квадратный метр: {e}")
        return None  # Ensure that the function doesn't crash and returns a safe value

async def get_price_dynamics(days=7):
    """
    Возвращает динамику роста/падения цен за последние n дней.
    """
    try:
        now = datetime.now()
        start_date = now - timedelta(days=days)

        pipeline = [
            {"$match": {"_id": {"$gte": ObjectId.from_datetime(start_date)}, "price": {"$exists": True}}},
            {
                "$project": {
                    "price": {
                        "$toDouble": {
                            "$replaceAll": {
                                "input": {"$trim": {"input": "$price", "chars": " AZN"}},
                                "find": " ",
                                "replacement": ""
                            }
                        }
                    }
                }
            },
            {"$group": {"_id": None, "average_price": {"$avg": "$price"}}},
        ]

        result = await ads_collection.aggregate(pipeline).to_list(1)
        logging.info(f"Pipeline result: {result}")
        return result[0]["average_price"] if result else None
    except Exception as e:
        logging.error(f"Ошибка при расчете динамики цен: {e}")
        return None  # Ensure safe return even in case of error