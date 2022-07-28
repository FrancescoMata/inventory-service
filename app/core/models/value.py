from typing import Any

from pydantic import BaseModel


class Value(BaseModel):
    id: "str"
    value: "str"
