import datetime

from core.config.db.mongodb import get_views_collection
from core.models.pricing import PricingBase, PricingRequestBase
from core.services.assets import get_assets_by_partial_descriptor, create_options, get_values_from_assets_by_field, \
    create_value


async def populate_view(pricing_request: "PricingBase") -> PricingBase:
    pricing_response = pricing_request

    initial_descriptor = pricing_request.descriptor
    assets = await get_assets_by_partial_descriptor(dict(pricing_request))

    inputs_section = next(filter(lambda section: section.name == 'inputs', pricing_response.manifest.sections))

    for element in inputs_section.elements:
        if element.id in initial_descriptor:
            element.value = create_value(initial_descriptor[element.id])
            element.locked = True
        list_of_values = get_values_from_assets_by_field(initial_descriptor, assets, element.id)
        if len(list_of_values) > 0:
            element.validation['options'] = create_options(element.label, False, list_of_values)

    return pricing_response


async def initiate_view(pricing_request: "PricingRequestBase") -> PricingBase:
    collection = await get_views_collection()

    initial_descriptor = pricing_request.descriptor
    assets = await get_assets_by_partial_descriptor(dict(pricing_request))

    view = await collection.find_one({"assetClass": pricing_request.asset_class})
    pricing_response = PricingBase.parse_obj(view)
    pricing_response.timestamp = datetime.datetime.now()

    inputs_section = next(filter(lambda section: section.name == 'inputs', pricing_response.manifest.sections))

    for element in inputs_section.elements:
        if element.id in initial_descriptor:
            element.value = create_value(initial_descriptor[element.id])
            element.locked = True
        else:
            list_of_values = get_values_from_assets_by_field(initial_descriptor, assets, element.id)
            if len(list_of_values) > 0:
                element.validation['options'] = create_options(element.label, False, list_of_values)

    return pricing_response
