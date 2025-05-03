"""
bili-jeans application
"""
import asyncio
import datetime
import functools
import json
import logging
from pathlib import Path
from typing import cast, Callable, List, Optional, Tuple, Union

from ..core.constants import FormatNumberValue
from ..core.download import (
    create_audio_task,
    create_cover_task,
    create_danmaku_task,
    create_subtitle_tasks,
    create_video_task
)
from ..core.factory import parse_web_view_url
from ..core.pages import get_ugc_pages
from ..core.proxy import get_ugc_play, get_ugc_player, get_ugc_view
from ..core.schemes import (
    GetUGCPlayResponse,
    GetUGCPlayerResponse,
    PageData,
    WebViewMetaData
)


logger = logging.getLogger(__name__)


SPLIT_LINE = '#' * 100


def split_line_wrapper(func: Callable) -> Callable:

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger.info(SPLIT_LINE)
        result = await func(*args, **kwargs)
        logger.info(SPLIT_LINE)
        return result

    return wrapper


async def run(
    url: str,
    directory: str,
    page_indexes: Optional[List[int]] = None,
    qn: Optional[int] = None,
    reverse_qn: bool = False,
    codec_id: Optional[int] = None,
    reverse_codec: bool = False,
    bit_rate_id: Optional[int] = None,
    reverse_bit_rate: bool = False,
    enable_danmaku: bool = False,
    enable_cover: bool = False,
    enable_subtitle: bool = False,
    sess_data: Optional[str] = None
):
    view_meta = await _get_view_meta_by_url(url)
    if view_meta is None:
        return
    _ = await _get_view_data(view_meta.bvid, view_meta.aid, sess_data)
    pages = await _get_pages(view_meta, page_indexes, sess_data)

    dir_p = Path(directory)
    assert dir_p.is_dir() is True  # given path should be a directory

    tasks = [
        asyncio.create_task(
            _download_page(
                page,
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
        for page in pages
    ]
    _ = await asyncio.gather(*tasks)


@split_line_wrapper
async def _get_view_meta_by_url(url: str) -> Optional[WebViewMetaData]:
    logger.info('Parsing resource ID...')
    try:
        metadata = await parse_web_view_url(url)
    except ValueError as e:
        logger.info(f'Parse resource ID failed: <{str(e)}>')
        return None
    logger.info(f'Parse resource ID succeed: {json.dumps(metadata.model_dump())}')
    return metadata


@split_line_wrapper
async def _get_view_data(
    bvid: Optional[str] = None,
    aid: Optional[int] = None,
    sess_data: Optional[str] = None
) -> None:
    logger.info('Parsing resource...')
    ugc_view = await get_ugc_view(
        bvid=bvid,
        aid=aid,
        sess_data=sess_data
    )
    if ugc_view.code != 0:
        logger.info(f'Parsing resource failed: {ugc_view.message}')
        return None
    data_dm = ugc_view.data
    assert data_dm is not None
    logger.info(f'Resource title: {data_dm.title}')
    logger.info(f'Resource URL: {data_dm.view_url}')
    logger.info(
        'Resource publish time: {}'.format(
            datetime.datetime.fromtimestamp(
                data_dm.pubdate
            ).strftime("%Y-%m-%d %H:%M:%S")
        )
    )
    logger.info(f'Resource uploader: {data_dm.owner.name}')
    logger.info(f'Resource uploader homepage URL: {data_dm.owner.homepage_url}')
    return None


@split_line_wrapper
async def _get_pages(
    metadata: WebViewMetaData,
    page_indexes: Optional[List[int]] = None,
    sess_data: Optional[str] = None
) -> List[PageData]:
    logger.info('Parsing pages...')
    pages = await get_ugc_pages(metadata, sess_data)
    for page in pages:
        page_duration: Optional[str] = None
        if page.duration is not None:
            hours, remaining = divmod(page.duration, 3600)
            minutes, seconds = divmod(remaining, 60)
            page_duration = f'{hours:02d}:{minutes:02d}:{seconds:02d}'
        tips = ' | '.join([
            item for item in (
                f'P{page.idx}',
                f'{page.cid}',
                page.title,
                page_duration
            ) if item is not None
        ])
        logger.info(tips)
    selected_pages_label = 'all'
    if page_indexes is not None:
        selected_pages_idx = list(
            filter(
                lambda page_idx: page_idx in page_indexes,
                [page.idx for page in pages]
            )
        )
        selected_pages_label = ', '.join(map(str, selected_pages_idx))
        pages = [page for page in pages if page.idx in selected_pages_idx]
    logger.info(f'Selected pages: {selected_pages_label}')
    return pages


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
