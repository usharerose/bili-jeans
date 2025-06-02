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

from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import print_formatted_text
from prompt_toolkit.formatted_text import HTML

from ..core.constants import FormatNumberValue, FILE_EXT_MP4
from ..core.download import (
    create_audio_task,
    create_cover_task,
    create_danmaku_task,
    create_subtitle_tasks,
    create_video_task,
    list_cli_bit_rate_options,
    list_cli_codec_qn_filtered_options,
    list_cli_quality_options
)
from ..core.factory import parse_web_view_url
from ..core.muxer import mux_streams
from ..core.pages import get_ugc_pages
from ..core.proxy import get_ugc_play, get_ugc_player, get_ugc_view
from ..core.schemes import (
    GetUGCPlayResponse,
    GetUGCPlayerResponse,
    PageData,
    WebViewMetaData
)


__all__ = ['run']


logger = logging.getLogger(__name__)


SPLIT_LINE = '#' * 100


def split_line_wrapper(
    func: Optional[Callable] = None,
    *,
    split_char: str = '#',
    length: int = 100
) -> Callable:
    def decorator(f: Callable) -> Callable:

        @functools.wraps(f)
        async def wrapper(*args, **kwargs):
            split_line = split_char * length
            logger.info(split_line)
            result = await f(*args, **kwargs)
            logger.info(split_line)
            return result

        return wrapper

    if func is not None:
        return decorator(func)

    return decorator


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
    skip_mux: bool = False,
    preserve_original: bool = False,
    sess_data: Optional[str] = None,
    interactive: bool = False
) -> None:
    view_meta = await _get_view_meta_by_url(url)
    if view_meta is None:
        return
    _ = await _get_view_data(view_meta.bvid, view_meta.aid, sess_data)
    if interactive:
        # get all of pages
        pages = await _get_pages(
            view_meta,
            sess_data=sess_data,
            interactive=True
        )
    else:
        pages = await _get_pages(view_meta, page_indexes, sess_data)

    dir_p = Path(directory)
    assert dir_p.is_dir() is True  # given path should be a directory

    for page in pages:
        if not interactive:
            await _download_page(
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
                skip_mux,
                preserve_original,
                sess_data
            )
        else:
            await _download_page_interactively(page, dir_p, sess_data)
    logger.info('All pages downloaded')


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
    sess_data: Optional[str] = None,
    interactive: bool = False
) -> List[PageData]:
    """
    get all of pages of one streaming resource
    when interactive is True,
    'page_indexes' would be ignored
    """
    logger.info('Parsing pages...')

    pages = await get_ugc_pages(metadata, sess_data)
    for page in pages:
        page_duration: Optional[str] = None
        if page.duration is not None:
            hours, remaining = divmod(page.duration, 3600)
            minutes, seconds = divmod(remaining, 60)
            page_duration = f'{hours:02d}:{minutes:02d}:{seconds:02d}'
        fmt_fields = [
            f'P{page.idx}',
            f'{page.cid}',
            page.title,
            page_duration
        ]
        logger.info(' | '.join([field for field in fmt_fields if field is not None]))

    if interactive:
        return pages

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


@split_line_wrapper
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
    enable_cover: bool = False,
    enable_subtitle: bool = False,
    skip_mux: bool = False,
    preserve_original: bool = False,
    sess_data: Optional[str] = None
) -> None:
    """
    create async tasks to download various resources of one page
    """
    logger.info(f'Downloading page {page_data.idx}...')

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
    for task in tasks:
        if task is not None:
            await task.run()

    if not skip_mux:
        output_file_p = dir_path.joinpath(
            f'{page_data.bvid}/{page_data.cid}.mux{FILE_EXT_MP4}'
        )
        await mux_streams(
            output_file=str(output_file_p),
            url=page_data.page_url,
            title=page_data.title,
            description=page_data.description,
            author_name=page_data.owner_name,
            publish_date=page_data.pubdate,
            video_file=str(video_task.file_path) if video_task else None,
            audio_file=str(audio_task.file_path) if audio_task else None,
            cover_file=str(cover_task.file_path) if cover_task else None,
            overwrite=True,
            preserve_original=preserve_original
        )
        if not preserve_original and output_file_p.exists():
            output_file_p.rename(dir_path.joinpath(
                f'{page_data.bvid}/{page_data.cid}{FILE_EXT_MP4}'
            ))

    logger.info(f'Downloaded page {page_data.idx} succeed')
    return None


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


@split_line_wrapper
async def _download_page_interactively(
    page_data: PageData,
    dir_path: Path,
    sess_data: Optional[str] = None
) -> None:
    """
    create async tasks to download various resources of one page
    by command-line interaction
    """
    page_label = f'P{page_data.idx}. {page_data.title}'
    to_download_page = await _ensure_process_or_not(f'download {page_label}')
    if not to_download_page:
        return None

    ugc_play, ugc_player = await _get_page_resources(
        page_data,
        sess_data
    )

    to_download_video = await _ensure_process_or_not('download video')
    video_file_p = None
    if to_download_video:
        video_file_p = await _download_video_interactively(
            page_data, ugc_play, dir_path
        )

    to_download_audio = await _ensure_process_or_not('download audio')
    audio_file_p = None
    if to_download_audio:
        audio_file_p = await _download_audio_interactively(
            page_data, ugc_play, dir_path
        )

    to_download_danmaku = await _ensure_process_or_not('download danmaku')
    if to_download_danmaku:
        danmaku_task = create_danmaku_task(page_data, dir_path)
        await danmaku_task.run()

    to_download_cover = await _ensure_process_or_not('download cover')
    cover_file_p = None
    if to_download_cover:
        cover_task = create_cover_task(page_data, dir_path)
        await cover_task.run()
        cover_file_p = cover_task.file_path

    to_download_subtitle = await _ensure_process_or_not('download subtitle')
    if to_download_subtitle:
        subtitle_tasks = create_subtitle_tasks(
            page_data, ugc_player, dir_path
        )
        await asyncio.gather(*[task.run() for task in subtitle_tasks])

    to_mux = await _ensure_process_or_not('mux video and audio')
    if to_mux:
        to_preserve_original = await _ensure_process_or_not(
            'reserve original video and audio files'
        )
        output_file_p = dir_path.joinpath(
            f'{page_data.bvid}/{page_data.cid}.mux{FILE_EXT_MP4}'
        )
        await mux_streams(
            output_file=str(output_file_p),
            url=page_data.page_url,
            title=page_data.title,
            description=page_data.description,
            author_name=page_data.owner_name,
            publish_date=page_data.pubdate,
            video_file=str(video_file_p) if video_file_p else None,
            audio_file=str(audio_file_p) if audio_file_p else None,
            cover_file=str(cover_file_p) if cover_file_p else None,
            overwrite=True,
            preserve_original=to_preserve_original
        )
        if not to_preserve_original and output_file_p.exists():
            output_file_p.rename(dir_path.joinpath(
                f'{page_data.bvid}/{page_data.cid}{FILE_EXT_MP4}'
            ))

    logger.info(f'Downloaded P{page_data.idx} succeed')
    return None


async def _ensure_process_or_not(
    process_name: str
) -> bool:
    logger.info(f'Whether {process_name} or not?')

    result = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: prompt('(y/n): ').strip().lower()
    )
    feedback = False
    if result in ('y', 'yes'):
        feedback = True

    if not feedback:
        logger.info(f'Skipping {process_name}')
    return feedback


async def _download_video_interactively(
    page_data: PageData,
    ugc_play: Optional[GetUGCPlayResponse],
    dir_path: Path,
) -> Optional[Path]:
    """
    choose the resource
    by quality and codec cascadingly
    """
    qn = await _choose_qn(ugc_play)
    if qn is None:
        return None
    codec_id = await _choose_qn_filtered_codec_id(qn, ugc_play)
    video_task = create_video_task(
        page_data,
        ugc_play,
        dir_path,
        qn,
        codec_id=codec_id
    )
    if video_task is None:
        return None

    await video_task.run()
    return video_task.file_path


async def _get_selected_quality_options(
    options: Optional[List[Tuple[str, int]]] = None
) -> Optional[Tuple[str, int]]:
    if options is None:
        logger.info('No available options')
        return None

    logger.info('Available options are:')
    for option in options:
        label, _ = option
        logger.info(label)

    while True:
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: prompt("Please choose your option by serial number: ").strip()
            )
            idx = int(result) - 1
            if 0 <= idx < len(options):
                return options[idx]
            print_formatted_text(HTML('<yellow>Please input effective number</yellow>'))
        except ValueError:
            print_formatted_text(HTML('<yellow>Please input numeric value</yellow>'))


async def _choose_qn(
    ugc_play: Optional[GetUGCPlayResponse]
) -> Optional[int]:
    logger.info('Choose the video quality from the following options')
    options = list_cli_quality_options(ugc_play)
    option = await _get_selected_quality_options(options)
    if option is None:
        return None
    _, qn = option
    return qn


async def _choose_qn_filtered_codec_id(
    qn: int,
    ugc_play: Optional[GetUGCPlayResponse]
) -> Optional[int]:
    logger.info('Choose the video codec from the following options')
    options = list_cli_codec_qn_filtered_options(qn, ugc_play)
    option = await _get_selected_quality_options(options)
    if option is None:
        return None
    _, codec_id = option
    return codec_id


async def _download_audio_interactively(
    page_data: PageData,
    ugc_play: Optional[GetUGCPlayResponse],
    dir_path: Path,
) -> Optional[Path]:
    """
    choose the resource
    by quality and codec cascadingly
    """
    bit_rate_id = await _choose_bit_rate(ugc_play)
    audio_task = create_audio_task(
        page_data,
        ugc_play,
        dir_path,
        bit_rate_id
    )
    if audio_task is None:
        return None
    await audio_task.run()
    return audio_task.file_path


async def _choose_bit_rate(
    ugc_play: Optional[GetUGCPlayResponse]
) -> Optional[int]:
    logger.info('Choose the audio bit rate from the following options')
    options = list_cli_bit_rate_options(ugc_play)
    option = await _get_selected_quality_options(options)
    if option is None:
        return None
    _, bit_rate_id = option
    return bit_rate_id
