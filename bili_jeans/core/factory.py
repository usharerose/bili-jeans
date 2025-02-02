"""
Factory on instance according to resource type
"""
import logging
import re
from typing import Optional
from urllib.parse import urlparse

import aiohttp
from aiohttp import ClientResponse

from .constants import HEADERS, TIMEOUT
from .schemes import WebViewMetaData


logger = logging.getLogger(__name__)


BVID_LENGTH = 9
WEB_VIEW_URL_UGC_BVID_PATTERN = re.compile(fr'/video/(BV1[a-zA-Z0-9]{{{BVID_LENGTH}}})')
WEB_VIEW_URL_UGC_AVID_PATTERN = re.compile(r'/video/av(\d+)')


WEB_VIEW_URL_ID_TYPE_MAPPING = {
    WEB_VIEW_URL_UGC_BVID_PATTERN: ('bvid', str),
    WEB_VIEW_URL_UGC_AVID_PATTERN: ('aid', int)
}


async def parse_web_view_url(url: str) -> WebViewMetaData:
    """
    extract metadata from web view URL

    before parsing it, the HTTP request to the given Url
    would be sent for getting the redirecting destination Url
    """
    dest_url = url
    response: Optional[ClientResponse] = None
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                url,
                headers=HEADERS,
                timeout=aiohttp.ClientTimeout(total=float(TIMEOUT)),
                allow_redirects=False
            ) as resp:
                response = resp
        except Exception:
            logger.warning(
                f'Parse web view Url failed when initiate HTTP request: {url}'
            )
            pass
    if response is not None:
        dest_url = response.headers.get('location', url)

    url_path = urlparse(dest_url).path
    for path_pattern in (WEB_VIEW_URL_UGC_BVID_PATTERN, WEB_VIEW_URL_UGC_AVID_PATTERN):
        search_result = path_pattern.search(url_path)
        if search_result:
            metadata = WebViewMetaData()
            field_name, func_name = WEB_VIEW_URL_ID_TYPE_MAPPING[path_pattern]
            metadata.__setattr__(
                field_name,
                func_name(search_result.group(1))
            )
            return metadata
    raise ValueError(
        f'Invalid Url. source Url: {url}, destination Url: {dest_url}'
    )
