"""
create download task for video of UGC page
"""
import logging
from pathlib import Path
from typing import List, Optional, Tuple

from .download_task import BaseCoroutineDownloadTask, StreamDownloadTask
from ..constants import (
    CodecId,
    FILE_EXT_MP4,
    QualityNumber
)
from ..schemes import GetUGCPlayResponse, PageData
from ..schemes.ugc_play import GetUGCPlayData, GetUGCPlayDataDash
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
        url = _get_video_from_durl(ugc_play.data)
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

    fmt_fields = [
        f'{QualityNumber.from_value(video.id_field).quality_name}',
        f'{video.width}x{video.height}',
        f'{CodecId.from_value(video.codecid).quality_name}',
        f'{video.frame_rate} fps' if video.frame_rate is not None else 'unknown'
    ]
    logger.info(
        f'[Chosen video stream]: '
        f'{" | ".join([field for field in fmt_fields if field is not None])}'
    )
    return video.base_url


def _get_video_from_durl(
    ugc_play_data: GetUGCPlayData
) -> str:
    """
    When the resource is unpurchased but can be previewed,
    would return it via durl
    """
    durl = ugc_play_data.durl
    assert durl is not None
    video, *_ = durl

    tips = ' | '.join([
        item for item in (
            f'{QualityNumber.from_value(ugc_play_data.quality).quality_name}',
            'unknown',
            f'{CodecId.from_value(ugc_play_data.video_codecid).quality_name}',
            'unknown'
        ) if item is not None
    ])
    logger.info(
        f'[Chosen video stream]: {tips}'
    )
    return video.url


def list_cli_quality_options(
    ugc_play: Optional[GetUGCPlayResponse]
) -> Optional[List[Tuple[str, int]]]:
    if ugc_play is None:
        return None
    if ugc_play.data is None:
        logger.error(
            f'No UGC play data: [{ugc_play.code}] {ugc_play.message}'
        )
        return None

    if ugc_play.data.dash is not None:
        return _list_all_quality_from_dash(
            ugc_play.data.dash
        )
    if ugc_play.data.durl is not None:
        return _list_all_quality_from_durl(ugc_play.data)

    logger.error('No any UGC video data')
    return None


def list_cli_codec_qn_filtered_options(
    qn: int,
    ugc_play: Optional[GetUGCPlayResponse]
) -> Optional[List[Tuple[str, int]]]:
    if ugc_play is None:
        return None
    if ugc_play.data is None:
        logger.error(
            f'No UGC play data: [{ugc_play.code}] {ugc_play.message}'
        )
        return None

    if ugc_play.data.dash is not None:
        return _list_codec_qn_filtered_from_dash(
            qn,
            ugc_play.data.dash
        )
    if ugc_play.data.durl is not None:
        return _list_codec_qn_filtered_from_durl(
            qn,
            ugc_play.data
        )

    logger.error('No any UGC video data')
    return None


def _list_all_quality_from_dash(
    dash: GetUGCPlayDataDash
) -> List[Tuple[str, int]]:
    videos = dash.video
    qn_set = set()
    result = []
    counter = 0
    for video in videos:
        if video.id_field in qn_set:
            continue
        qn_set.add(video.id_field)
        result.append((
            f'{counter + 1}. {QualityNumber.from_value(video.id_field).quality_name}',
            video.id_field
        ))
        counter += 1
    return result


def _list_codec_qn_filtered_from_dash(
    qn: int,
    dash: GetUGCPlayDataDash
) -> Optional[List[Tuple[str, int]]]:
    videos = [video for video in dash.video if video.id_field == qn]
    if not videos:
        return None

    codec_id_set = set()
    result = []
    counter = 0
    for video in videos:
        if video.codecid in codec_id_set:
            continue
        codec_id_set.add(video.codecid)
        result.append((
            f'{counter + 1}. {CodecId.from_value(video.codecid).quality_name}',
            video.codecid
        ))
        counter += 1
    return result


def _list_all_quality_from_durl(
    ugc_play_data: GetUGCPlayData
) -> List[Tuple[str, int]]:
    return [(
        f'1. {QualityNumber.from_value(ugc_play_data.quality).quality_name}',
        ugc_play_data.quality
    )]


def _list_codec_qn_filtered_from_durl(
    qn: int,
    ugc_play_data: GetUGCPlayData
) -> Optional[List[Tuple[str, int]]]:
    if ugc_play_data.quality != qn:
        return None

    return [(
        f'1. {CodecId.from_value(ugc_play_data.video_codecid).quality_name}',
        ugc_play_data.video_codecid
    )]
