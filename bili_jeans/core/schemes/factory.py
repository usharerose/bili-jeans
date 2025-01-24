"""
Scheme definition of Bilibili view's metadata
"""
from typing import Optional

from pydantic import BaseModel


class WebViewMetaData(BaseModel):

    aid: Optional[int] = None
    bvid: Optional[str] = None


class PageData(BaseModel):
    """
    standard metadata of page which is the finest resource from Bilibili
    """
    aid: Optional[int] = None
    bvid: Optional[str] = None
    cid: int
    title: str
    duration: Optional[int]     # unit is second
