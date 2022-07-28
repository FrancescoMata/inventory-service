from pydantic import BaseModel, Field

from core.models.options import Options


class Validation(BaseModel):
    type: "str" = Field(...)
    valid: "bool" = Field(...)
    placeholder: "str" = Field(...)
    options: "Options" = Field(None)
