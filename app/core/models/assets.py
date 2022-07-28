from pydantic import BaseModel, Field


class Meta(BaseModel):
    display_name: str = Field(..., alias='displayName')
    image: str = Field(...)


class Assets(BaseModel):
    asset_class: str = Field(..., alias="assetClass")
    descriptor: dict = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "assetClass": "electronics",
                "enabled": False,
                "descriptor": {
                    "condition": "good",
                    "locked": "locked",
                    "name": "iPad Pro 3 (2018) 11 WiFi 16GB"
                },
                "meta": {
                    "displayName": "iPad Pro 3 (2018) 11 WiFi 16GB",
                    "image": "https://via.placeholder.com/300.png/09f/fff"
                }
            }
        }
