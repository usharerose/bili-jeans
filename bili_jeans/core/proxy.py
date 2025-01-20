"""
Proxy Interface on Bilibili API
"""
import json
from typing import Dict, Optional

import aiohttp

from .schemes import GetUGCViewResponse


HEADERS = {
    'origin': 'https://www.bilibili.com',
    'referer': 'https://www.bilibili.com/',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'accept': 'application/json, text/plain, */*',
    'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"macOS"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site'
}
TIMEOUT = 5


URL_WEB_UGC_VIEW = 'https://api.bilibili.com/x/web-interface/view'


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
            headers=HEADERS
        ) as response:
            content = await response.read()
            data = json.loads(content.decode('utf-8'))
            return data
