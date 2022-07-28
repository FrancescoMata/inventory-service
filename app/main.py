from core.config.db.mongodb_utils import connect_to_mongo, close_mongo_connection
import pydantic
from bson.objectid import ObjectId
from fastapi import FastAPI

from api.v1.api import router as api_router

pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str


app = FastAPI(title='search-service')
app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)
app.include_router(api_router, prefix='/v1')
