"""
Scheme definition of the response from https://api.bilibili.com/x/player/wbi/v2
"""
from typing import List, Optional

from pydantic import BaseModel, Field

from .base import BaseResponseModel


class GetUGCPlayerDataSubtitleSubtitleItem(BaseModel):

    id_field: int = Field(..., alias='id')
    lan: str
    lan_doc: str
    is_lock: bool
    subtitle_url: str
    subtitle_url_v2: str
    type_field: int = Field(..., alias='type')
    ai_type: int
    ai_status: int


class GetUGCPlayerDataSubtitle(BaseModel):

    allow_submit: bool
    lan: str
    lan_doc: str
    subtitles: List[GetUGCPlayerDataSubtitleSubtitleItem]


class GetUGCPlayerData(BaseModel):

    aid: int
    bvid: str
    cid: int
    subtitle: GetUGCPlayerDataSubtitle


class GetUGCPlayerResponse(BaseResponseModel):

    data: Optional[GetUGCPlayerData] = None
