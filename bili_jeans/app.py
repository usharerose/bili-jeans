"""
bili-jeans application
"""
import asyncio
from pathlib import Path
from typing import Optional

from .core.constants import FormatNumberValue
from .core.download import download_resource
from .core.factory import parse_web_view_url
from .core.pages import get_ugc_pages
from .core.proxy import get_ugc_play
from .core.schemes import PageData


async def run(
    url: str,
    dir_path: str,
    sess_data: Optional[str] = None
) -> None:
    dir_p = Path(dir_path)
    assert dir_p.is_dir() is True  # given path should be a directory

    metadata = await parse_web_view_url(url)
    pages = await get_ugc_pages(metadata, sess_data)

    tasks = [
        asyncio.create_task(_download_page(page_data, dir_p, sess_data))
        for page_data in pages
    ]
    _ = await asyncio.gather(*tasks)


async def _download_page(
    page_data: PageData,
    dir_path: Path,
    sess_data: Optional[str] = None
) -> None:
    ugc_play = await get_ugc_play(
        cid=page_data.cid,
        bvid=page_data.bvid,
        aid=page_data.aid,
        fnval=FormatNumberValue.get_dash_full_fnval(),
        sess_data=sess_data
    )
    if ugc_play.data is None:
        raise
    video, *_ = ugc_play.data.dash.video

    file_p = dir_path.joinpath(f'{page_data.cid}.mp4')
    await download_resource(url=video.base_url, file=str(file_p))
