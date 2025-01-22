"""
Scheme definition of the response from https://api.bilibili.com/x/web-interface/wbi/view
"""
from typing import List, Optional

from pydantic import BaseModel, Field

from .base import BaseResponseModel


class GetUGCViewDataOwner(BaseModel):
    """
    Bilibili user metadata
    """
    face: str  # Profile icon's source URL
    mid: int   # User ID
    name: str  # User name


class GetUGCViewPagesItem(BaseModel):
    """
    Metadata of a page which is an individual video streaming
    """
    cid: int       # cid of this page
    duration: int  # Total seconds of this page
    page: int      # Serial num of this page
    part: str      # Title of this page


class GetUGCViewDataUGCSeasonSectionsItemEpisodesItemARC(BaseModel):
    """
    Episode arc
    """
    aid: int       # AV ID of video
    ctime: int     # Unix timestamp when video contributed
    desc: str      # legacy version episode description
    duration: int  # Total seconds of episode
    pic: str       # URL of episode cover
    pubdate: int   # Unix timestamp when video published (audited)
    title: str     # Title of episode


class GetUGCViewDataUGCSeasonSectionsItemEpisodesItem(BaseModel):
    """
    Episode data
    """
    aid: int                                                 # AV ID of video
    arc: GetUGCViewDataUGCSeasonSectionsItemEpisodesItemARC  # Episode arc
    bvid: str                                                # BV ID of video
    cid: int                                                 # cid of video's 1P
    id_field: int = Field(..., alias='id')                   # episode ID, which links to a video
    page: GetUGCViewPagesItem                                # current page data
    pages: List[GetUGCViewPagesItem]                         # pages data
    season_id: int                                           # season ID
    section_id: int                                          # Section ID
    title: str                                               # episode title


class GetUGCViewDataUGCSeasonSectionsItem(BaseModel):
    """
    Section data
    """
    episodes: List[GetUGCViewDataUGCSeasonSectionsItemEpisodesItem]  # Episode data
    id_field: int = Field(..., alias='id')                           # Identifier of the section
    season_id: int                                                   # Identifier of the season
    title: str                                                       # section title


class GetUGCViewDataUGCSeason(BaseModel):
    """
    UGC season, and its own sections' data
    """
    cover: str                                           # URL of season cover
    ep_count: int                                        # Count of episodes
    id_field: int = Field(..., alias='id')               # season ID
    intro: str                                           # Introduction of the season
    mid: int                                             # User identifier of season owner
    sections: List[GetUGCViewDataUGCSeasonSectionsItem]  # Divided section data
    title: str                                           # season title


class GetUGCViewData(BaseModel):
    """
    'data' field, only defines part of necessary fields
    """
    aid: int                                              # AV ID of video
    bvid: str                                             # BV ID of video
    cid: int                                              # cid of video's 1P
    ctime: int                                            # Unix timestamp when video contributed
    desc: str                                             # legacy version video description
    duration: int                                         # Total seconds of video
    is_season_display: bool                               # be included in season or not
    owner: GetUGCViewDataOwner                            # Owner of the video
    pages: List[GetUGCViewPagesItem]                      # Pages of the video, one or multiple
    pic: str                                              # URL of video cover
    pubdate: int                                          # Unix timestamp when video published (audited)
    title: str                                            # Title of video
    ugc_season: Optional[GetUGCViewDataUGCSeason] = None  # related UGC season's info with other videos


class GetUGCViewResponse(BaseResponseModel):
    """
    On 'code' field,

    0：success, and has 'data'
    -400：request error
    -403：authentication limit
    -404：video unavailable
    62002：video invisible
    62004：video in review
    """
    data: Optional[GetUGCViewData] = None
