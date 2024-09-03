from parsers.database import ads_collection
from bson import ObjectId
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)

async def get_average_price_per_square_meter():
    """
    Returns the average price per square meter based on the ads in the database.
    """
    try:
        pipeline = [
            {"$match": {"price": {"$exists": True}, "title": {"$regex": r"\d+\s*m²"}}},
            {
                "$project": {
                    "price": {
                        "$convert": {
                            "input": {"$arrayElemAt": [{"$split": ["$price", " "]}, 0]},
                            "to": "double",
                            "onError": None,
                            "onNull": None
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
            {"$match": {"square_meter": {"$ne": 0}, "price": {"$ne": None}}},
            {"$project": {"price_per_square_meter": {"$divide": ["$price", "$square_meter"]}}},
            {"$group": {"_id": None, "avg_price_per_sqm": {"$avg": "$price_per_square_meter"}}},
        ]
        
        result = await ads_collection.aggregate(pipeline).to_list(1)
        logging.info(f"Pipeline result: {result}")
        return result[0]["avg_price_per_sqm"] if result else None
    except Exception as e:
        logging.error(f"Error calculating the average price per square meter: {e}")
        raise

async def get_price_dynamics(days=7):
    """
    Returns the price dynamics for the last `n` days.
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
        logging.error(f"Error calculating price dynamics: {e}")
        raise