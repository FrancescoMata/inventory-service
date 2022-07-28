from fastapi import APIRouter
from fastapi import FastAPI
from api.v1.endpoints.items import router as items_router
from api.v1.endpoints.gbt import router as gbt_router
from fastapi.responses import JSONResponse

router = APIRouter()
router.include_router(items_router)
router.include_router(gbt_router)
