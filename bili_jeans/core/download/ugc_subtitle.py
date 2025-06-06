"""
create download task for subtitle of UGC page
"""
import logging
from pathlib import Path
from typing import List, Optional

from .download_task import (
    BaseCoroutineDownloadTask,
    StreamDownloadTask,
    SRTSubtitleDownloadTask
)
from ..constants import FILE_EXT_JSON, FILE_EXT_SRT
from ..schemes import GetUGCPlayerResponse, PageData


logger = logging.getLogger(__name__)


def create_subtitle_tasks(
    page_data: PageData,
    ugc_player: Optional[GetUGCPlayerResponse],
    dir_path: Path
) -> List[BaseCoroutineDownloadTask]:
    download_tasks: List[BaseCoroutineDownloadTask] = []

    if ugc_player is None:
        return download_tasks
    if ugc_player.data is None:
        logger.error(
            f'No UGC player data for {page_data.cid} of {page_data.bvid}: '
            f'[{ugc_player.code}] {ugc_player.message}'
        )
        return download_tasks

    for subtitle in ugc_player.data.subtitle.subtitles:
        url = 'https:' + subtitle.subtitle_url
        filename_wo_ext = f'{page_data.bvid}/{page_data.cid}.{subtitle.id_field}'

        raw_filename = f'{filename_wo_ext}{FILE_EXT_JSON}'
        raw_file_p = dir_path.joinpath(raw_filename)
        download_raw_task = StreamDownloadTask(
            url=url,
            file=str(raw_file_p)
        )
        srt_filename = f'{filename_wo_ext}{FILE_EXT_SRT}'
        srt_file_p = dir_path.joinpath(srt_filename)
        download_srt_task = SRTSubtitleDownloadTask(
            url=url,
            file=str(srt_file_p)
        )

        logger.info(
            f'[Chosen subtitle source]: {subtitle.lan_doc}'
        )

        download_tasks.extend([download_raw_task, download_srt_task])
    return download_tasks
