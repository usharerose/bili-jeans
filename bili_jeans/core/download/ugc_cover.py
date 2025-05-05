"""
create download task for cover of UGC page
"""
from pathlib import Path

from .download_task import (
    BaseCoroutineDownloadTask,
    StreamDownloadTask
)
from ..constants import FILE_EXT_JPG
from ..schemes import PageData


def create_cover_task(
    page_data: PageData,
    dir_path: Path
) -> BaseCoroutineDownloadTask:
    url = page_data.cover

    filename = f'{page_data.bvid}/{page_data.cid}{FILE_EXT_JPG}'
    file_p = dir_path.joinpath(filename)

    download_task = StreamDownloadTask(
        url=url,
        file=str(file_p)
    )
    return download_task
