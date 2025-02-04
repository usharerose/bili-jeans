"""
Proxy Interface on Bilibili API
"""
import json
from typing import Dict, Optional

import aiohttp

from .constants import (
    HEADERS,
    TIMEOUT,
    URL_WEB_UGC_PLAY,
    URL_WEB_UGC_PLAYER,
    URL_WEB_UGC_VIEW
)
from .schemes import GetUGCPlayResponse, GetUGCPlayerResponse, GetUGCViewResponse


async def get_ugc_view(
    bvid: Optional[str] = None,
    aid: Optional[int] = None,
    sess_data: Optional[str] = None
) -> GetUGCViewResponse:
    data = await get_ugc_view_response(bvid, aid, sess_data)
    return GetUGCViewResponse.model_validate(data)


async def get_ugc_view_response(
    bvid: Optional[str] = None,
    aid: Optional[int] = None,
    sess_data: Optional[str] = None
) -> Dict:
    """
    get UGC resource meta info which is with '/video' namespace
    support being requested byf one of BV ID (which has higher priority) and AV ID
    refer to https://www.bilibili.com/read/cv5167957/?spm_id_from=333.976.0.0)
    """
    if all([id_val is None for id_val in (bvid, aid)]):
        raise ValueError("One of bvid and aid is required")

    params: Dict = {}
    if bvid is not None:
        params.update({'bvid': bvid})
    else:
        params.update({'aid': aid})

    async with aiohttp.ClientSession() as session:
        if sess_data is not None:
            session.cookie_jar.update_cookies({'SESSDATA': sess_data})
        async with session.get(
            URL_WEB_UGC_VIEW,
            params=params,
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=float(TIMEOUT))
        ) as response:
            content = await response.read()
            data = json.loads(content.decode('utf-8'))
            return data


async def get_ugc_play(
    cid: int,
    bvid: Optional[str] = None,
    aid: Optional[int] = None,
    qn: Optional[int] = None,
    fnval: int = 16,
    fourk: int = 1,
    sess_data: Optional[str] = None
) -> GetUGCPlayResponse:
    data = await get_ugc_play_response(cid, bvid, aid, qn, fnval, fourk, sess_data)
    return GetUGCPlayResponse.model_validate(data)


async def get_ugc_play_response(
    cid: int,
    bvid: Optional[str] = None,
    aid: Optional[int] = None,
    qn: Optional[int] = None,
    fnval: int = 16,
    fourk: int = 1,
    sess_data: Optional[str] = None
) -> Dict:
    """
    get UGC play resource info which is with '/video' namespace
    :param cid: Identifier of codec
    :type cid: int
    :param bvid: BV ID of video
    :type bvid: Optional[str]
    :param aid: AV ID of video
    :type aid: Optional[int]
    :param qn: Format quality number of play resource
    :type qn: Optional[int]
    :param fnval: integer type value of binary bitmap standing for multi-attribute combination
    :type fnval: int
    :param fourk: 4K or not
    :type fourk: int
    :param sess_data: cookie of Bilibili user, SESSDATA
    :type sess_data: str
    :return: dict, UGC play response data
    """
    if all([id_val is None for id_val in (bvid, aid)]):
        raise ValueError("One of bvid and aid is required")

    params: Dict = {}
    if bvid is not None:
        params.update({'bvid': bvid})
    else:
        params.update({'aid': aid})
    if qn is not None:
        params.update({'qn': qn})
    params.update({
        'cid': cid,
        'fnval': fnval,
        'fourk': fourk
    })

    async with aiohttp.ClientSession() as session:
        if sess_data is not None:
            session.cookie_jar.update_cookies({'SESSDATA': sess_data})
        async with session.get(
            URL_WEB_UGC_PLAY,
            params=params,
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=float(TIMEOUT))
        ) as response:
            content = await response.read()
            data = json.loads(content.decode('utf-8'))
            return data


async def get_ugc_player(
    cid: int,
    bvid: Optional[str] = None,
    aid: Optional[int] = None,
    season_id: Optional[int] = None,
    ep_id: Optional[int] = None,
    sess_data: Optional[str] = None
) -> GetUGCPlayerResponse:
    data = await get_ugc_player_response(
        cid,
        bvid,
        aid,
        season_id,
        ep_id,
        sess_data
    )
    return GetUGCPlayerResponse.model_validate(data)


async def get_ugc_player_response(
    cid: int,
    bvid: Optional[str] = None,
    aid: Optional[int] = None,
    season_id: Optional[int] = None,
    ep_id: Optional[int] = None,
    sess_data: Optional[str] = None
) -> Dict:
    """
    get UGC web player metadata which is with '/video' namespace
    :param cid: Identifier of codec
    :type cid: int
    :param bvid: BV ID of video
    :type bvid: Optional[str]
    :param aid: AV ID of video
    :type aid: Optional[int]
    :param season_id: Season ID of bangumi
    :type season_id: Optional[int]
    :param ep_id: Episode ID of bangumi
    :type ep_id: Optional[int]
    :param sess_data: cookie of Bilibili user, SESSDATA
    :type sess_data: str
    :return: dict, UGC player response data
    """
    if all([id_val is None for id_val in (bvid, aid)]):
        raise ValueError("One of bvid and aid is required")

    params: Dict = {}
    if bvid is not None:
        params.update({'bvid': bvid})
    else:
        params.update({'aid': aid})
    if season_id is not None:
        params.update({'season_id': season_id})
    if ep_id is not None:
        params.update({'ep_id': ep_id})
    params.update({'cid': cid})

    async with aiohttp.ClientSession() as session:
        if sess_data is not None:
            session.cookie_jar.update_cookies({'SESSDATA': sess_data})
        async with session.get(
            URL_WEB_UGC_PLAYER,
            params=params,
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=float(TIMEOUT))
        ) as response:
            content = await response.read()
            data = json.loads(content.decode('utf-8'))
            return data
