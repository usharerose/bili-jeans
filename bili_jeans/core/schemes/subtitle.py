"""
Scheme definition of the subtitle from remote URL
"""
from typing import List

from pydantic import BaseModel, Field


class SubTitleBodyItem(BaseModel):

    from_field: float = Field(..., alias='from')
    to: float
    location: int
    content: str


class SubTitle(BaseModel):

    font_size: float
    font_color: str
    background_alpha: float
    background_color: str
    body: List[SubTitleBodyItem]
