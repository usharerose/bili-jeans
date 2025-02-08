"""
create download task for cover of UGC page
"""
from mimetypes import guess_extension
from pathlib import Path
from typing import Optional

from .download_task import (
    BaseCoroutineDownloadTask,
    StreamDownloadTask
)
from ..constants import MIME_TYPE_JPEG
from ..schemes import PageData


def create_cover_task(
    page_data: PageData,
    dir_path: Path
) -> Optional[BaseCoroutineDownloadTask]:
    url = page_data.cover
    mime_type = MIME_TYPE_JPEG

    filename = f'{page_data.bvid}/{page_data.cid}{guess_extension(mime_type) or ""}'
    file_p = dir_path.joinpath(filename)

    download_task = StreamDownloadTask(
        url=url,
        file=str(file_p)
    )
    return download_task
