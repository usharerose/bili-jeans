"""
Scheme definition of the response from https://api.bilibili.com/x/player/wbi/playurl
"""
from typing import List, Optional, Union

from pydantic import BaseModel, Field

from .base import BaseResponseModel, DashMediaItem


class GetUGCPlayDataDashFlac(BaseModel):
    """
    Hi-Res audio data
    """
    audio: Optional[DashMediaItem] = None
    display: bool                          # illustrate Hi-Res or not


class GetUGCPlayDataDashDolby(BaseModel):
    """
    Dolby audio data
    """
    audio: Optional[List[DashMediaItem]] = None
    # 1 is normal, 2 is panoramic
    # for cheese, could be 'NONE'
    type_field: Union[int, str] = Field(..., alias='type')


class GetUGCPlayDataDash(BaseModel):
    """
    UGC stream play's DASH
    """
    audio: Optional[List[DashMediaItem]] = None    # null when resource has no audio
    dolby: GetUGCPlayDataDashDolby                 # Dolby audio
    duration: int                                  # resource duration which unit is second
    flac: Optional[GetUGCPlayDataDashFlac] = None  # High quality audio
    video: List[DashMediaItem]                     # video


class GetUGCPlayDataDUrlItem(BaseModel):
    """
    Common UGC play resource data
    """
    backup_url: List[str]  # URLs of backup resources
    length: int            # duration of resource which unit is millisecond
    order: int             # order number of resource
    size: int              # size of resource, unit is byte
    url: str               # URL of resource


class GetUGCPlayDataSupportFormatsItem(BaseModel):
    """
    supported UGC play's qualities
    """
    codecs: Optional[List[str]]                     # list of supported codec
    display_desc: str                               # display description
    format_field: str = Field(..., alias='format')  # file format extension
    new_description: str                            # complete description
    quality: int                                    # quality number


class GetUGCPlayData(BaseModel):
    """
    'data' field, only defines part of necessary fields
    """
    video_codecid: int
    dash: Optional[GetUGCPlayDataDash] = None                # raw resources
    durl: Optional[List[GetUGCPlayDataDUrlItem]] = None      # video-audio combined resources
    quality: int
    support_formats: List[GetUGCPlayDataSupportFormatsItem]  # visible supported formats


class GetUGCPlayResponse(BaseResponseModel):
    """
    On 'code' field,

    0：success, and has 'data'
    -400：request error
    -404：video unavailable
    """
    data: Optional[GetUGCPlayData] = None
