"""Images schemas for API validation."""

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class ImagesBase(BaseModel):
    """Base images schema."""

    image: str
    is_active: bool = True


class ImagesCreate(ImagesBase):
    """Images creation schema."""

    pass


class Images(ImagesBase):
    """Images response schema."""

    id: int
    post_id: int
    created: datetime
    updated: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
