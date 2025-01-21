"""
Factory on instance according to resource type
"""
import re
from typing import Optional
from urllib.parse import urlparse

from pydantic import BaseModel


BVID_LENGTH = 9
WEB_VIEW_URL_UGC_BVID_PATTERN = re.compile(fr'/video/(BV1[a-zA-Z0-9]{{{BVID_LENGTH}}})')
WEB_VIEW_URL_UGC_AVID_PATTERN = re.compile(r'/video/av(\d+)')


WEB_VIEW_URL_ID_TYPE_MAPPING = {
    WEB_VIEW_URL_UGC_BVID_PATTERN: ('bvid', str),
    WEB_VIEW_URL_UGC_AVID_PATTERN: ('aid', int)
}


class WebViewMetaData(BaseModel):

    aid: Optional[int] = None
    bvid: Optional[str] = None


def parse_web_view_url(url: str) -> WebViewMetaData:
    """
    extract metadata from web view URL
    """
    url_path = urlparse(url).path
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
    raise ValueError(f'Invalid Url: {url}')
