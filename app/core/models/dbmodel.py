from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field


class ObjectIdStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(str(v)):
            return ValueError(f"Not a valid ObjectId: {v}")
        return ObjectId(str(v))


class DBModelMixin(BaseModel):
    id: Optional[ObjectIdStr] = Field(default=ObjectId(), alias="_id")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectIdStr: lambda x: str(x), ObjectId: lambda x: str(x)}
