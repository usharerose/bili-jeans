"""
create download task for danmaku of UGC page
"""
from mimetypes import guess_extension
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode, urlparse

from .download_task import (
    BaseCoroutineDownloadTask,
    StreamDownloadTask
)
from ..constants import (
    MIME_TYPE_XML,
    URL_WEB_DANMAKU
)
from ..schemes import PageData


def create_danmaku_task(
    page_data: PageData,
    dir_path: Path
) -> Optional[BaseCoroutineDownloadTask]:
    url = urlparse(URL_WEB_DANMAKU)._replace(
        query=urlencode({'oid': page_data.cid})
    ).geturl()
    mime_type = MIME_TYPE_XML

    filename = f'{page_data.bvid}/{page_data.cid}{guess_extension(mime_type) or ""}'
    file_p = dir_path.joinpath(filename)

    download_task = StreamDownloadTask(
        url=url,
        file=str(file_p)
    )
    return download_task
