import uuid
from typing import List

from core.config.db.mongodb import get_assets_collection
from core.models.options import Options
from core.models.value import Value


async def get_assets_by_partial_descriptor(query: "dict") -> List[dict]:
    collection = await get_assets_collection()
    query_descriptor = {f'descriptor.{k}': v for k, v in query['descriptor'].items()}
    assets = await collection.find({"assetClass": query['asset_class'],
                                    "enabled": False, **query_descriptor}).to_list(1000)
    return assets


def get_values_from_assets_by_field(initial_descriptor: "dict", assets: "List[dict]", field: "str"):
    descriptors = list(map(lambda x: x['descriptor'], assets))
    if initial_descriptor in descriptors:
        descriptors.remove(initial_descriptor)
    values = set(map(lambda x: x[field], descriptors)) if all(field in asset for asset in descriptors) else {}
    return list(values)


def create_options(name: "str", display_name: "bool", values_list="List[str]"):
    values_list = [create_value(val) for val in values_list]
    return Options(id=uuid.uuid4().hex, name=name, displayName=display_name, values=values_list)


def create_value(value: "str"):
    return Value(id=value.lower().replace(' ', '_'), value=value)
