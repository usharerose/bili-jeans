"""
bili-jeans application
"""
import asyncio
from pathlib import Path
from typing import Optional, Set

from .core.constants import FormatNumberValue, QualityNumber
from .core.download import download_resource
from .core.factory import parse_web_view_url
from .core.pages import get_ugc_pages
from .core.proxy import get_ugc_play
from .core.schemes import PageData


async def run(
    url: str,
    dir_path: str,
    qn: Optional[int] = None,
    reverse_qn: bool = False,
    sess_data: Optional[str] = None
) -> None:
    dir_p = Path(dir_path)
    assert dir_p.is_dir() is True  # given path should be a directory

    metadata = await parse_web_view_url(url)
    pages = await get_ugc_pages(metadata, sess_data)

    tasks = [
        asyncio.create_task(_download_page(page_data, dir_p, qn, reverse_qn, sess_data))
        for page_data in pages
    ]
    _ = await asyncio.gather(*tasks)


async def _download_page(
    page_data: PageData,
    dir_path: Path,
    qn: Optional[int] = None,
    reverse_qn: bool = False,
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
    videos = ugc_play.data.dash.video

    avail_qn_set = set([video.id_field for video in videos])
    qn = _filter_avail_quality_number(avail_qn_set, qn, reverse_qn)
    videos = [video for video in videos if video.id_field == qn]
    video, *_ = videos

    file_p = dir_path.joinpath(f'{page_data.cid}.mp4')
    await download_resource(url=video.base_url, file=str(file_p))


def _filter_avail_quality_number(
    qn_set: Set[int],
    qn: Optional[int] = None,
    reverse_qn: bool = False
) -> int:
    """
    filter out the target quality number
    1. when no declared quality number, choose one from qn_set
       if reverse_qn is True, prefer the greatest one which represents the highest quality
       else the least one
    2. when given quality number doesn't match anyone in qn_set
       find the nearest one which lesser first, then greater one
    3. when given quality number exists in qn_set, return it
    """
    if len(qn_set) <= 0:
        raise ValueError('No alternative quality numbers')

    if qn is None:
        avail_qns = sorted(list(qn_set), reverse=reverse_qn)
        qn, *_ = avail_qns
        return qn

    # if given qn doesn't match any available qn in qn_set
    # find the nearest one which lesser first
    if qn not in qn_set:
        greater: Optional[int] = None
        lesser: Optional[int] = None
        for item in qn_set:
            if item > qn:
                greater = item if greater is None or greater > item else greater
            else:
                lesser = item if lesser is None or lesser < item else lesser
        qn = lesser or greater
    if qn is None:
        raise ValueError('No available quality number')

    return qn
