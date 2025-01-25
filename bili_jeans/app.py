"""
bili-jeans application
"""
import asyncio
from pathlib import Path
from typing import Optional, Set, Type, Union

from .core.constants import (
    BitRateId,
    CodecId,
    FormatNumberValue,
    QualityNumber
)
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
    qn = _filter_avail_quality_id(QualityNumber, avail_qn_set, qn, reverse_qn)
    videos = [video for video in videos if video.id_field == qn]
    video, *_ = videos

    file_p = dir_path.joinpath(f'{page_data.cid}.mp4')
    await download_resource(url=video.base_url, file=str(file_p))


def _filter_avail_quality_id(
    quality_class: Union[
        Type[BitRateId],
        Type[CodecId],
        Type[QualityNumber]
    ],
    quality_set: Set[int],
    quality_id: Optional[int] = None,
    reverse: bool = False
) -> int:
    """
    filter out the target quality ID
    1. when no declared quality ID, choose one from quality set
       if reverse is True, prefer the greatest one on order which represents the highest quality
       else the least one
    2. when given quality ID doesn't match anyone in quality set
       find the nearest one which lesser first, then greater one
    3. when given quality ID exists in quality set, return it
    """
    if len(quality_set) <= 0:
        raise ValueError('No alternative quality IDs')

    try:
        _ = quality_class.from_value(quality_id)
    except ValueError:
        quality_id = None

    quality_ids = [
        quality_class.from_value(_quality_id)
        for _quality_id in quality_set
    ]

    if quality_id is None:
        avail_quality_items = sorted(
            quality_ids,
            key=lambda _q_item: _q_item.quality_order,
            reverse=reverse
        )
        quality_item, *_ = avail_quality_items
        return quality_item.quality_id

    if quality_id not in quality_set:
        greater: Optional[quality_class] = None
        lesser: Optional[quality_class] = None
        quality_id_obj = quality_class.from_value(quality_id)
        for item in quality_ids:
            if item > quality_id_obj:
                greater = item if greater is None or greater > item else greater
            else:
                lesser = item if lesser is None or lesser < item else lesser
        quality_id_obj = lesser or greater
        return quality_id_obj.quality_id

    return quality_id
