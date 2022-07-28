
from datetime import datetime
from grp import struct_group
import json
from operator import index
from sqlite3 import Date
from time import time
from typing import List, Union
from h11 import Data
import pandas as pd
from fastapi.responses import FileResponse


from fastapi import APIRouter, Depends, Body, Query
from motor.motor_asyncio import AsyncIOMotorCollection
from numpy import NaN, number

from core.config.db.mongodb import get_items_collection
from core.config.db.mongodb import get_packages_collection
from core.models.assets import Assets
from core.services.assets import get_assets_by_partial_descriptor

router = APIRouter()


@router.get("/items", response_description="List all assets", tags=['assets'])
async def list_assets(
    assetsCollection: AsyncIOMotorCollection = Depends(
        get_items_collection),
    packagesCollection: AsyncIOMotorCollection = Depends(
        get_packages_collection),
        fromD: str = Query(default=None),
        toD: str = Query(default=None),
        region: str = Query(default=None)
):
    fromDate = datetime.strptime(fromD, "%Y-%m-%d")
    toDate = datetime.strptime(toD, "%Y-%m-%d")
    assets = await assetsCollection.find({
        'updatedAt': {'$gte': datetime(fromDate.year, fromDate.month, fromDate.day),
                      '$lt': datetime(toDate.year, toDate.month, toDate.day)},
        'status': 'reviewed',
        'rejectedManually': False,
        'price': {'$gt': 0},
        'category': {'$ne': 'electronics'},
        'condition': {'$not': {'$eq': 'E'}}}).to_list(length=None)

    packages = await packagesCollection.find({'updatedAt': {'$gte': datetime(fromDate.year, fromDate.month, fromDate.day),
                                                            '$lt': datetime(toDate.year, toDate.month, toDate.day)}}).to_list(length=None)
    dfPackages = pd.DataFrame(packages).explode('items')
    dfAssets = pd.DataFrame(assets).drop_duplicates(subset=['_id'])

    mapItems_packages = pd.merge(
        dfAssets, dfPackages, left_on="sellerId", right_on="sellerId", how="left").drop_duplicates(subset=['_id_x'])
    currency_code = pd.Series({
        'UK': 'GBP',
        'US': 'USD',
        'IT': 'EUR'
    })

    pictures = mapItems_packages['pictures'].map(
        lambda x: list(map(lambda y: y['url'], x)))

    # id, size, brand, size_standard, gender, material, color, category, subcategory, name, description, picture_1, picture_2, picture_3, country, net_price, currency_code, tier
    newDataFrame = pd.DataFrame({
        "id": mapItems_packages['_id_x'],
        "size": mapItems_packages['size'],
        "brand": mapItems_packages['brand'],
        "size_standard": mapItems_packages['countrySize'],
        "gender": mapItems_packages['gender'],
        "material": mapItems_packages['material'],
        "color": mapItems_packages['color'],
        "category": mapItems_packages['category'],
        "subcategory": mapItems_packages['subcategory'],
        "name": mapItems_packages['name'],
        "description": mapItems_packages['description'],
        'picture_1': pictures.map(lambda x: x[0] if len(x) > 0 else 'NA'),
        'picture_2': pictures.map(lambda x: x[1] if len(x) > 1 else 'NA'),
        'picture_3': pictures.map(lambda x: x[2] if len(x) > 2 else 'NA'),
        "country": mapItems_packages['country_x'],
        "net_price": mapItems_packages['price_x'],
        "currency_code": mapItems_packages['country_x'].map(currency_code)
    })
    newDataFrame = newDataFrame.drop_duplicates(['id'])

    result_df = newDataFrame.loc[(newDataFrame['country'] == region.upper())]

    result_df.to_csv(f'data/{str(fromD)}-{str(toD)}-{str(region)}.csv')
    # # df = pd.read_csv(str(fromD) + '-' + str(toD) + '-' + str(region) + '.csv')
    # csv_file = open(str(fromD) + '-' + str(toD) +
    #                 '-' + str(region) + '.csv', 'wb')
    return FileResponse(f'data/{str(fromD)}-{str(toD)}-{str(region)}.csv', media_type='application/octet-stream', filename=f'{str(fromD)}-{str(toD)}-{str(region)}.csv')

    # return assets
