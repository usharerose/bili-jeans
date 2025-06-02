"""
finest Bilibili resource granularity
"""
from typing import List, Optional

from .proxy import get_ugc_view
from .schemes import PageData, WebViewMetaData


async def get_ugc_pages(
    view_meta: WebViewMetaData,
    sess_data: Optional[str] = None
) -> List[PageData]:
    ugc_view = await get_ugc_view(
        bvid=view_meta.bvid,
        aid=view_meta.aid,
        sess_data=sess_data
    )
    if ugc_view.code != 0:
        raise ValueError(ugc_view.message)

    pages = []
    assert ugc_view.data is not None
    for idx, item in enumerate(ugc_view.data.pages):
        page = PageData(
            idx=item.page,
            aid=ugc_view.data.aid,
            bvid=ugc_view.data.bvid,
            cid=item.cid,
            title=item.part,
            cover=ugc_view.data.pic,
            duration=item.duration,
            description=ugc_view.data.desc if idx == 0 else '',
            owner_name=ugc_view.data.owner.name,
            pubdate=ugc_view.data.pubdate
        )
        pages.append(page)
    return pages
