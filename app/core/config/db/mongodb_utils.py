import logging

from motor.motor_asyncio import AsyncIOMotorClient

from core.config.settings import settings
from core.config.db.mongodb import database


async def connect_to_mongo():
    logging.info("Trying to connect to mongo.")
    database.client = AsyncIOMotorClient(str(settings.MONGODB_URL))
    logging.info("Connected to mongo succesfully")


async def close_mongo_connection():
    logging.info("Trying to close connection to mongo")
    database.client.close()
    logging.info("Shutdown succesfully")
