from datetime import datetime
from typing import List

from pydantic import Field, BaseModel

from core.models.dbmodel import DBModelMixin
from core.models.element import BaseElement


class Section(BaseModel):
    name: "str" = Field(...)
    elements: List[BaseElement] = Field(...)


class Manifest(BaseModel):
    version: "str" = Field(...)
    sections: "List[Section]" = Field(None)


class PricingBase(DBModelMixin):
    schema_version: "str" = Field(..., alias='schemaVersion')
    timestamp: "datetime" = Field(...)
    user_id: "str" = Field(..., alias='userId')
    asset_class: "str" = Field(..., alias='assetClass')
    descriptor: "dict" = Field(None)
    manifest: "Manifest" = Field(...)


class PricingRequestBase(BaseModel):
    user_id: "str" = Field(..., alias='userId')
    asset_class: "str" = Field(..., alias='assetClass')
    descriptor: "dict" = Field(...)
