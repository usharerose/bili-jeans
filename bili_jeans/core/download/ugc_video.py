"""
create download task for video of UGC page
"""
import logging
from pathlib import Path
from typing import List, Optional

from .download_task import BaseCoroutineDownloadTask, StreamDownloadTask
from ..constants import (
    CodecId,
    FILE_EXT_MP4,
    QualityNumber
)
from ..schemes import GetUGCPlayResponse, PageData
from ..schemes.ugc_play import GetUGCPlayDataDash, GetUGCPlayDataDUrlItem
from ..utils import filter_avail_quality_id


logger = logging.getLogger(__name__)


def create_video_task(
    page_data: PageData,
    ugc_play: Optional[GetUGCPlayResponse],
    dir_path: Path,
    qn: Optional[int] = None,
    reverse_qn: bool = False,
    codec_id: Optional[int] = None,
    reverse_codec: bool = False
) -> Optional[BaseCoroutineDownloadTask]:
    if ugc_play is None:
        return None
    if ugc_play.data is None:
        logger.error(
            f'No UGC play data for {page_data.cid} of {page_data.bvid}: '
            f'[{ugc_play.code}] {ugc_play.message}'
        )
        return None

    if ugc_play.data.dash is not None:
        url = _get_video_from_dash(
            ugc_play.data.dash,
            qn,
            reverse_qn,
            codec_id,
            reverse_codec
        )
    elif ugc_play.data.durl is not None:
        url = _get_video_from_durl(ugc_play.data.durl)
    else:
        logger.error(
            f'No any UGC video data for {page_data.cid} of {page_data.bvid}'
        )
        return None

    filename = f'{page_data.bvid}/{page_data.cid}{FILE_EXT_MP4}'
    file_p = dir_path.joinpath(filename)

    download_task = StreamDownloadTask(
        url=url,
        file=str(file_p)
    )
    return download_task


def _get_video_from_dash(
    dash: GetUGCPlayDataDash,
    qn: Optional[int] = None,
    reverse_qn: bool = False,
    codec_id: Optional[int] = None,
    reverse_codec: bool = False
) -> str:
    videos = dash.video

    avail_qn_set = set([video.id_field for video in videos])
    qn = filter_avail_quality_id(QualityNumber, avail_qn_set, qn, reverse_qn)
    videos = [video for video in videos if video.id_field == qn]
    video, *_ = videos

    avail_codec_id_set = set([video.codecid for video in videos])
    codec_id = filter_avail_quality_id(CodecId, avail_codec_id_set, codec_id, reverse_codec)
    videos = [video for video in videos if video.codecid == codec_id]
    video, *_ = videos

    return video.base_url


def _get_video_from_durl(
    durl: List[GetUGCPlayDataDUrlItem]
) -> str:
    """
    When the resource is unpurchased but can be previewed,
    would return it via durl
    """
    video, *_ = durl
    return video.url
