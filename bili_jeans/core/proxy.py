"""
Proxy Interface on Bilibili API
"""
import json
from typing import Dict, Optional

import aiohttp

from .constants import HEADERS, TIMEOUT, URL_WEB_UGC_VIEW
from .schemes import GetUGCViewResponse


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
