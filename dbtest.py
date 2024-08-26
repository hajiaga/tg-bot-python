from parsers.database import save_ad_to_db, check_if_ad_exists
from parsers.bina_parser import parse_bina_ads

async def test_mongo():
    ads = parse_bina_ads()
    for ad in ads:
        if not await check_if_ad_exists(ad):
            await save_ad_to_db(ad)
            print(f"Объявление сохранено: {ad}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_mongo())