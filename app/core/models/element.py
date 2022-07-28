from enum import Enum

from pydantic import BaseModel, Field

from core.models.validation import Validation
from core.models.value import Value


class ElementType(str, Enum):
    input = "INPUT"
    image = "IMAGE"
    boolean = "BOOLEAN"
    dropdown = "DROPDOWN"
    searchable_dropdown = "SEARCHABLE_DROPDOWN"
    hierarchical_dropdown = "HIERARCHICAL_DROPDOWN"


class BaseElement(BaseModel):
    id: "str" = Field(...)
    type: "str" = Field(...)
    label: "str" = Field(...)
    locked: "bool" = Field(...)
    required: "bool" = Field(...)
    value: Value = Field(None)
    validation: "dict" = Field(None)
