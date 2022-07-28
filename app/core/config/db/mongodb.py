from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase

from core.config.settings import settings


class DataBase:
    client: AsyncIOMotorClient = None


database = DataBase()


async def get_database() -> AsyncIOMotorDatabase:
    return database.client[settings.DATABASE_NAME]


async def get_assets_collection() -> AsyncIOMotorCollection:
    return database.client[settings.DATABASE_NAME][settings.ASSET_COLLECTION]


async def get_views_collection() -> AsyncIOMotorCollection:
    return database.client[settings.DATABASE_NAME][settings.VIEWS_COLLECTION]


async def get_sizes_collection() -> AsyncIOMotorCollection:
    return database.client[settings.DATABASE_NAME][settings.SIZES_COLLECTION]


async def get_items_collection() -> AsyncIOMotorCollection:
    return database.client[settings.DATABASE_NAME][settings.ITEMS_COLLECTION]


async def get_packages_collection() -> AsyncIOMotorCollection:
    return database.client[settings.DATABASE_NAME][settings.PACKAGES_COLLECTION]


async def get_orders_collection() -> AsyncIOMotorCollection:
    return database.client[settings.DATABASE_NAME][settings.ORDERS_COLLECTION]
