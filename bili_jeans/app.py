"""
bili-jeans application
"""
from pathlib import Path
from typing import Optional

from .core.constants import FormatNumberValue
from .core.download import download_resource
from .core.factory import parse_web_view_url
from .core.proxy import get_ugc_play, get_ugc_view


async def run(
    url: str,
    dir_path: str,
    sess_data: Optional[str] = None
):
    dir_p = Path(dir_path)
    assert dir_p.is_dir() is True  # given path should be a directory

    metadata = await parse_web_view_url(url)
    ugc_view = await get_ugc_view(bvid=metadata.bvid, aid=metadata.aid)
    if ugc_view.data is None:
        raise
    ugc_view_data = ugc_view.data
    ugc_play = await get_ugc_play(
        cid=ugc_view_data.cid,
        bvid=ugc_view_data.bvid,
        aid=ugc_view_data.aid,
        fnval=FormatNumberValue.get_dash_full_fnval(),
        sess_data=sess_data
    )
    if ugc_play.data is None:
        raise
    video, *_ = ugc_play.data.dash.video
    source_url = video.base_url

    file_p = dir_p.joinpath(f'{ugc_view_data.cid}.mp4')
    await download_resource(url=source_url, file=str(file_p))
