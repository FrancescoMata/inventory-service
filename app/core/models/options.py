import uuid
from typing import List, Any

from pydantic import Field, BaseModel

from core.models.value import Value


class Options(BaseModel):
    id: "str" = Field(...)
    name: "str" = Field(...)
    display_name: "bool" = Field(..., alias='displayName')
    values: List[Value] = Field(...)
