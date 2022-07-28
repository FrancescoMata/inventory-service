from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    MONGODB_URL: str = Field(..., env='MONGODB_URL')
    DATABASE_NAME: str = Field(..., env='DATABASE_NAME')
    ITEMS_COLLECTION: str = Field(..., env='ITEMS_COLLECTION')
    PACKAGES_COLLECTION: str = Field(..., env='PACKAGES_COLLECTION')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


@lru_cache()
def get_settings():
    return Settings()


load_dotenv()
settings = get_settings()
