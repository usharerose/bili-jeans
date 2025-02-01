"""
bili-jeans application
"""
import asyncio
from mimetypes import guess_extension
from pathlib import Path
from typing import List, Optional, Set, Type

from .core.constants import (
    BitRateId,
    CodecId,
    FormatNumberValue,
    QualityNumber,
    QualityId
)
from .core.download import download_resource
from .core.factory import parse_web_view_url
from .core.pages import get_ugc_pages
from .core.proxy import get_ugc_play
from .core.schemes import PageData
from .core.schemes.ugc_play import DashMediaItem


async def run(
    url: str,
    dir_path: str,
    qn: Optional[int] = None,
    reverse_qn: bool = False,
    codec_id: Optional[int] = None,
    reverse_codec: bool = False,
    bit_rate_id: Optional[int] = None,
    reverse_bit_rate: bool = False,
    sess_data: Optional[str] = None
) -> None:
    dir_p = Path(dir_path)
    assert dir_p.is_dir() is True  # given path should be a directory

    metadata = await parse_web_view_url(url)
    pages = await get_ugc_pages(metadata, sess_data)

    tasks = [
        asyncio.create_task(
            _download_page(
                page_data,
                dir_p,
                qn,
                reverse_qn,
                codec_id,
                reverse_codec,
                bit_rate_id,
                reverse_bit_rate,
                sess_data
            )
        )
        for page_data in pages
    ]
    _ = await asyncio.gather(*tasks)


async def _download_page(
    page_data: PageData,
    dir_path: Path,
    qn: Optional[int] = None,
    reverse_qn: bool = False,
    codec_id: Optional[int] = None,
    reverse_codec: bool = False,
    bit_rate_id: Optional[int] = None,
    reverse_bit_rate: bool = False,
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
    dash = ugc_play.data.dash
    assert dash is not None
    videos = dash.video

    avail_qn_set = set([video.id_field for video in videos])
    qn = _filter_avail_quality_id(QualityNumber, avail_qn_set, qn, reverse_qn)
    videos = [video for video in videos if video.id_field == qn]
    video, *_ = videos

    avail_codec_id_set = set([video.codecid for video in videos])
    codec_id = _filter_avail_quality_id(CodecId, avail_codec_id_set, codec_id, reverse_codec)
    videos = [video for video in videos if video.codecid == codec_id]
    video, *_ = videos
    video_file_ext = guess_extension(video.mime_type) or ''
    video_file_p = dir_path.joinpath(f'{page_data.cid}{video_file_ext}')

    audios: List[DashMediaItem] = []
    if dash.audio is not None:
        audios.extend(dash.audio)
    flac = dash.flac
    if flac is not None and flac.audio is not None:
        audios.append(flac.audio)
    dolby = dash.dolby
    if dolby.audio is not None:
        audios.extend(dolby.audio)

    avail_bit_rate_set = set([audio.id_field for audio in audios])
    bit_rate_id = _filter_avail_quality_id(
        BitRateId,
        avail_bit_rate_set,
        bit_rate_id,
        reverse_bit_rate
    )
    audios = [audio for audio in audios if audio.id_field == bit_rate_id]
    audio, *_ = audios
    audio_file_ext = guess_extension(audio.mime_type) or ''
    audio_file_p = dir_path.joinpath(f'{page_data.cid}{audio_file_ext}')

    tasks = [
        asyncio.create_task(
            download_resource(**kwargs)
        ) for kwargs in [
            {
                'url': video.base_url,
                'file': str(video_file_p)
            },
            {
                'url': audio.base_url,
                'file': str(audio_file_p)
            }
        ]
    ]
    _ = await asyncio.gather(*tasks)


def _filter_avail_quality_id(
    quality_class: Type[QualityId],
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

    if quality_id is not None:
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
        greater: Optional[QualityId] = None
        lesser: Optional[QualityId] = None
        quality_id_obj = quality_class.from_value(quality_id)
        for item in quality_ids:
            if item > quality_id_obj:
                greater = item if greater is None or greater > item else greater
            else:
                lesser = item if lesser is None or lesser < item else lesser
        if lesser is not None:
            quality_id_obj = lesser
        elif greater is not None:
            quality_id_obj = greater
        return quality_id_obj.quality_id

    return quality_id
