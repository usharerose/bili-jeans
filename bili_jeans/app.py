"""
bili-jeans application
"""
import asyncio
import logging
from pathlib import Path
from typing import cast, Optional, Tuple, Union

from .core.constants import FormatNumberValue
from .core.download import (
    create_audio_task,
    create_cover_task,
    create_danmaku_task,
    create_subtitle_tasks,
    create_video_task
)
from .core.factory import parse_web_view_url
from .core.pages import get_ugc_pages
from .core.proxy import get_ugc_play, get_ugc_player
from .core.schemes import GetUGCPlayResponse, GetUGCPlayerResponse, PageData


logger = logging.getLogger(__name__)


async def run(
    url: str,
    dir_path: str,
    qn: Optional[int] = None,
    reverse_qn: bool = False,
    codec_id: Optional[int] = None,
    reverse_codec: bool = False,
    bit_rate_id: Optional[int] = None,
    reverse_bit_rate: bool = False,
    enable_danmaku: bool = False,
    enable_cover: bool = True,
    enable_subtitle: bool = True,
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
                enable_danmaku,
                enable_cover,
                enable_subtitle,
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
    enable_danmaku: bool = False,
    enable_cover: bool = True,
    enable_subtitle: bool = True,
    sess_data: Optional[str] = None
) -> None:
    ugc_play, ugc_player = await _get_page_resources(
        page_data,
        sess_data
    )

    video_task = create_video_task(
        page_data,
        ugc_play,
        dir_path,
        qn,
        reverse_qn,
        codec_id,
        reverse_codec
    )
    audio_task = create_audio_task(
        page_data,
        ugc_play,
        dir_path,
        bit_rate_id,
        reverse_bit_rate
    )
    danmaku_task = create_danmaku_task(page_data, dir_path) if enable_danmaku else None
    cover_task = create_cover_task(page_data, dir_path) if enable_cover else None
    subtitle_tasks = create_subtitle_tasks(
        page_data, ugc_player, dir_path
    ) if enable_subtitle else []

    tasks = [video_task, audio_task, danmaku_task, cover_task, *subtitle_tasks]
    _ = await asyncio.gather(*[task.run() for task in tasks if task is not None])


async def _get_page_resources(
    page_data: PageData,
    sess_data: Optional[str] = None
) -> Tuple[
    Optional[GetUGCPlayResponse],
    Optional[GetUGCPlayerResponse]
]:
    """
    get the response from UGC play and UGC player
    the response would be None when meet exception
    """
    get_ugc_play_coroutine = get_ugc_play(
        cid=page_data.cid,
        bvid=page_data.bvid,
        aid=page_data.aid,
        fnval=FormatNumberValue.get_dash_full_fnval(),
        sess_data=sess_data
    )
    get_ugc_player_coroutine = get_ugc_player(
        cid=page_data.cid,
        bvid=page_data.bvid,
        aid=page_data.aid,
        sess_data=sess_data
    )

    ugc_play: Optional[Union[GetUGCPlayResponse, BaseException]]
    ugc_player: Optional[Union[GetUGCPlayerResponse, BaseException]]
    ugc_play, ugc_player = cast(
        Tuple[
            Union[GetUGCPlayResponse, BaseException],
            Union[GetUGCPlayerResponse, BaseException]
        ],
        await asyncio.gather(
            *[
                get_ugc_play_coroutine,
                get_ugc_player_coroutine
            ], return_exceptions=True
        )
    )
    if isinstance(ugc_play, BaseException):
        logger.exception(
            f'meet exception when request UGC play data'
            f'for {page_data.cid} of {page_data.bvid}: {ugc_play}'
        )
        ugc_play = None
    if isinstance(ugc_player, BaseException):
        logger.exception(
            f'meet exception when request UGC player data'
            f'for {page_data.cid} of {page_data.bvid}: {ugc_player}'
        )
        ugc_player = None

    return ugc_play, ugc_player
