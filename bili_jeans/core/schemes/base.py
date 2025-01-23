"""
Scheme definition of the Bilibili API response
"""
from typing import List, Optional

from pydantic import BaseModel, Field


class BaseResponseModel(BaseModel):
    """
    Base of Bilibili API response
    """
    code: int = 0              # status code
    message: str = '0'         # error message
    ttl: Optional[int] = None


class DashMediaItem(BaseModel):
    """
    Digital media data
    """
    backup_url: List[str]                   # URLs of backup resources
    bandwidth: int                          # minimum of network bandwidth that needed
    base_url: str                           # resource URL
    codecid: int
    codecs: str
    height: int                             # 0 for audio
    id_field: int = Field(..., alias='id')
    mime_type: str
    width: int                              # 0 for audio
