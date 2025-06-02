"""
Scheme definition of Bilibili view's metadata
"""
from typing import Optional
from urllib.parse import urlencode, urlparse, urlunparse

from pydantic import BaseModel

from ..constants import (
    URL_WEB_HOST,
    URL_WEB_NAMESPACE_UGC
)


class WebViewMetaData(BaseModel):

    aid: Optional[int] = None
    bvid: Optional[str] = None


class PageData(BaseModel):
    """
    standard metadata of page which is the finest resource from Bilibili
    """
    idx: int
    aid: Optional[int] = None
    bvid: Optional[str] = None
    cid: int
    title: str
    cover: str
    duration: Optional[int]     # unit is second
    description: str
    owner_name: str
    # no publish date info for the pages, would fill view's here
    pubdate: int

    @property
    def page_url(self) -> str:
        if self.bvid is None:
            raise ValueError('BV ID of the page is required')

        unparsed_base = urlparse(URL_WEB_HOST)
        parts = (
            unparsed_base.scheme,
            unparsed_base.netloc,
            '/'.join([*(URL_WEB_NAMESPACE_UGC.split('/')), self.bvid]),
            '',
            urlencode({'p': self.idx}),
            ''
        )
        url = urlunparse(parts)
        return url
