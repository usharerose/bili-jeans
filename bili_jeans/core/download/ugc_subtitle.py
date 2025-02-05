"""
create download task for subtitle of UGC page
"""
import logging
from mimetypes import guess_extension
from pathlib import Path
from typing import List, Optional

from .download_task import (
    BaseCoroutineDownloadTask,
    GeneralCoroutineDownloadTask
)
from ..constants import MIME_TYPE_JSON
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
        mime_type = MIME_TYPE_JSON
        filename = f'{page_data.bvid}/{page_data.cid}.{subtitle.id_field}{guess_extension(mime_type) or ""}'
        file_p = dir_path.joinpath(filename)
        download_task = GeneralCoroutineDownloadTask(
            url=url,
            file=str(file_p)
        )
        download_tasks.append(download_task)
    return download_tasks
