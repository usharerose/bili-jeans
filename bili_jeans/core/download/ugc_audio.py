"""
create download task for audio of UGC page
"""
import logging
from pathlib import Path
from typing import List, Optional

from .download_task import (
    BaseCoroutineDownloadTask,
    StreamDownloadTask
)
from ..constants import BitRateId, FILE_EXT_M4A
from ..utils import filter_avail_quality_id
from ..schemes import GetUGCPlayResponse, PageData
from ..schemes.ugc_play import DashMediaItem, GetUGCPlayDataDash


logger = logging.getLogger(__name__)


def create_audio_task(
    page_data: PageData,
    ugc_play: Optional[GetUGCPlayResponse],
    dir_path: Path,
    bit_rate_id: Optional[int] = None,
    reverse_bit_rate: bool = False
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
        url = _get_audio_from_dash(
            ugc_play.data.dash,
            bit_rate_id,
            reverse_bit_rate
        )
    else:
        logger.error(
            f'No any UGC audio data for {page_data.cid} of {page_data.bvid}'
        )
        return None

    filename = f'{page_data.bvid}/{page_data.cid}{FILE_EXT_M4A}'
    file_p = dir_path.joinpath(filename)

    download_task = StreamDownloadTask(
        url=url,
        file=str(file_p)
    )
    return download_task


def _get_audio_from_dash(
    dash: GetUGCPlayDataDash,
    bit_rate_id: Optional[int] = None,
    reverse_bit_rate: bool = False
) -> str:
    audios: List[DashMediaItem] = []
    if dash.audio is not None:
        audios.extend(dash.audio)
    flac = dash.flac
    if flac is not None and flac.audio is not None:
        audios.append(flac.audio)
    dolby = dash.dolby
    if dolby.audio is not None:
        audios.extend(dolby.audio)

    avail_bit_rate_set = set([audio.id_field for audio in audios])
    bit_rate_id = filter_avail_quality_id(
        BitRateId,
        avail_bit_rate_set,
        bit_rate_id,
        reverse_bit_rate
    )
    audios = [audio for audio in audios if audio.id_field == bit_rate_id]
    audio, *_ = audios

    return audio.base_url
