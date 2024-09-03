from parsers.database import ads_collection
from bson import ObjectId
from datetime import datetime, timedelta
import logging
import re

logging.basicConfig(level=logging.INFO)

def extract_price(price_str):
    """
    Преобразует цену из строки в число.
    """
    try:
        return float(re.sub(r'[^\d]', '', price_str))  # Удаляет все символы, кроме цифр
    except ValueError:
        return None

def extract_square_meter(title_str):
    """
    Преобразует площадь из строки в число.
    """
    try:
        match = re.search(r'(\d+\.\d+|\d+)\s*m²', title_str)
        if match:
            return float(match.group(1))
        return None
    except ValueError:
        return None

async def get_average_price_per_square_meter():
    try:
        pipeline = [
            {"$match": {"price": {"$exists": True}, "title": {"$regex": r"\d+\s*m²"}}},
            {
                "$project": {
                    "price": {
                        "$toDouble": {
                            "$convert": {
                                "input": {"$substr": [{"$arrayElemAt": [{"$split": ["$price", " "]}, 0]}, 0, -1]},
                                "to": "double",
                                "onError": None,
                                "onNull": None
                            }
                        }
                    },
                    "square_meter": {
                        "$convert": {
                            "input": {"$arrayElemAt": [{"$split": ["$title", " m²"]}, 0]},
                            "to": "double",
                            "onError": None,
                            "onNull": None
                        }
                    },
                }
            },
            {"$project": {"price_per_square_meter": {"$divide": ["$price", "$square_meter"]}}},
            {"$match": {"price_per_square_meter": {"$ne": None, "$ne": 0}}},
            {"$group": {"_id": None, "avg_price_per_sqm": {"$avg": "$price_per_square_meter"}}},
        ]

        result = await ads_collection.aggregate(pipeline).to_list(1)
        logging.info(f"Pipeline result: {result}")
        return result[0]["avg_price_per_sqm"] if result else None
    except Exception as e:
        logging.error(f"Ошибка при расчете средней цены за квадратный метр: {e}")
        raise

async def get_price_dynamics(days=7):
    try:
        now = datetime.now()
        start_date = now - timedelta(days=days)

        pipeline = [
            {"$match": {"_id": {"$gte": ObjectId.from_datetime(start_date)}}},
            {"$project": {
                "price": {
                    "$toDouble": {
                        "$convert": {
                            "input": {"$substr": [{"$arrayElemAt": [{"$split": ["$price", " "]}, 0]}, 0, -1]},
                            "to": "double",
                            "onError": None,
                            "onNull": None
                        }
                    }
                }
            }},
            {"$group": {"_id": None, "average_price": {"$avg": "$price"}}},
        ]

        result = await ads_collection.aggregate(pipeline).to_list(1)
        logging.info(f"Pipeline result: {result}")
        return result[0]["average_price"] if result else None
    except Exception as e:
        logging.error(f"Ошибка при расчете динамики цен: {e}")
        raise