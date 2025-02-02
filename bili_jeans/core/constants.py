"""
Constants
"""
from enum import Enum, IntEnum
from functools import reduce
from typing import NamedTuple, Type


###############################
# Bilibili request parameters #
###############################
HEADERS = {
    'origin': 'https://www.bilibili.com',
    'referer': 'https://www.bilibili.com/',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'accept': 'application/json, text/plain, */*',
    'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"macOS"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site'
}
TIMEOUT = 5


################
# Bilibili API #
################
URL_WEB_UGC_PLAY = 'https://api.bilibili.com/x/player/wbi/playurl'
URL_WEB_UGC_VIEW = 'https://api.bilibili.com/x/web-interface/view'


class QualityItem(NamedTuple):

    quality_id: int
    quality_order: int

    def __le__(self, other: 'QualityItem') -> bool:  # type: ignore[override]
        return self.quality_order <= other.quality_order

    def __lt__(self, other: 'QualityItem') -> bool:  # type: ignore[override]
        return self.quality_order < other.quality_order

    def __ge__(self, other: 'QualityItem') -> bool:  # type: ignore[override]
        return self.quality_order >= other.quality_order

    def __gt__(self, other: 'QualityItem') -> bool:  # type: ignore[override]
        return self.quality_order > other.quality_order


class QualityId(QualityItem, Enum):

    @classmethod
    def from_value(cls: Type['QualityId'], value: int) -> 'QualityId':
        for item in cls:
            if item.quality_id == value:
                return item
        raise ValueError(f'Invalid given {cls.__name__}: {value}')


########################
# Video Quality Number #
########################
class QualityNumber(QualityId):
    """
    Format quality number of streaming resource, noneffective for DASH format
    | value | description | comment                                          |
    |-------+-------------+--------------------------------------------------|
    | 6     | 240P        | only support MP4                                 |
    | 16    | 360P        |                                                  |
    | 32    | 480P        |                                                  |
    | 64    | 720P        | Web default, login needed                        |
    | 74    | 720P60      | login needed                                     |
    | 80    | 1080P       | login needed                                     |
    | 112   | 1080P+      | VIP needed                                       |
    | 116   | 1080P60     | VIP needed                                       |
    | 120   | 4K          | VIP needed, `fnval&128=128` and `fourk=1`        |
    | 125   | HDR         | VIP needed, only support DASH, `fnval&64=64`     |
    | 126   | Dolby       | VIP needed, only support DASH, `fnval&512=512`   |
    | 127   | 8K          | VIP needed, only support DASH, `fnval&1024=1024` |
    """
    P240 = QualityItem(quality_id=6, quality_order=1)
    P360 = QualityItem(quality_id=16, quality_order=2)
    P480 = QualityItem(quality_id=32, quality_order=3)
    P720 = QualityItem(quality_id=64, quality_order=4)
    P720_60 = QualityItem(quality_id=74, quality_order=5)
    P1080 = QualityItem(quality_id=80, quality_order=6)
    PPLUS_1080 = QualityItem(quality_id=112, quality_order=7)
    P1080_60 = QualityItem(quality_id=116, quality_order=8)
    FOUR_K = QualityItem(quality_id=120, quality_order=9)
    HDR = QualityItem(quality_id=125, quality_order=10)
    DOLBY = QualityItem(quality_id=126, quality_order=11)
    EIGHT_K = QualityItem(quality_id=127, quality_order=12)

    @property
    def is_login_required(self) -> bool:
        return self >= self.P720

    @property
    def is_vip_required(self) -> bool:
        return self >= self.PPLUS_1080


#######################
# Format Number Value #
#######################
class FormatNumberValue(IntEnum):
    """
    integer type value of a binary bitmap standing for multi-attribute combination
    | value | description         | comment                                             |
    |-------+---------------------+-----------------------------------------------------|
    | 0     | FLV                 | exclusive with MP4 and DASH, deprecated             |
    | 1     | MP4                 | exclusive with FLV and DASH                         |
    | 16    | DASH                | exclusive with FLV and MP4                          |
    | 64    | HDR or not          | DASH is necessary, VIP needed, only H.265, `qn=125` |
    | 128   | 4K or not           | VIP needed, `fourk=1` and `qn=120`                  |
    | 256   | Dolby sound or not  | DASH is necessary, VIP needed                       |
    | 512   | Dolby vision or not | DASH is necessary, VIP needed                       |
    | 1024  | 8K or not           | DASH is necessary, VIP needed, `qn=127`             |
    | 2048  | AV1 codec or not    | DASH is necessary                                   |
    support 'or' for combination,
    e.g. DASH format, and HDR, fnval = 16 | 64 = 80
    """
    # FLV = 0           # deprecated
    MP4 = 1             # binary opposite to DASH
    DASH = 16
    HDR = 64
    FOUR_K = 128
    DOLBY_AUDIO = 256
    DOLBY_VISION = 512
    EIGHT_K = 1024
    AV1_ENCODE = 2048

    @classmethod
    def get_dash_full_fnval(cls) -> int:
        return reduce(
            lambda prev, cur: prev | cur,
            [item.value for item in cls if item != cls.MP4]
        )

    @classmethod
    def get_dash_fnval(
        cls,
        qn: int,
        is_dolby_audio: bool = False
    ) -> int:
        """
        get DASH-based format number value according to Quality Number
        :param qn: format quality number
        :type qn: int
        :param is_dolby_audio: request Dolby Audio or not
        :type is_dolby_audio: bool
        :return: int
        """
        result = cls.DASH.value
        if qn == QualityNumber.HDR.quality_id:
            result = result | cls.HDR
        if qn >= QualityNumber.FOUR_K.quality_id:
            result = result | cls.FOUR_K
        if is_dolby_audio:
            result = result | cls.DOLBY_AUDIO
        if qn == QualityNumber.DOLBY.quality_id:
            result = result | cls.DOLBY_VISION
        if qn == QualityNumber.EIGHT_K.quality_id:
            result = result | cls.EIGHT_K
        return result


############
# Codec Id #
############
class CodecId(QualityId):
    """
    AVC, which is avc1.64001E, not support 8K
    HEVC, which is hev1.1.6.L120.90
    AV1, which is av01.0.00M.10.0.110.01.01.01.0
    """
    AVC = QualityItem(quality_id=7, quality_order=1)
    HEVC = QualityItem(quality_id=12, quality_order=2)
    AV1 = QualityItem(quality_id=13, quality_order=3)


###############
# Bit Rate Id #
###############
class BitRateId(QualityId):
    """
    AVC, which is avc1.64001E, not support 8K
    HEVC, which is hev1.1.6.L120.90
    AV1, which is av01.0.00M.10.0.110.01.01.01.0
    """
    BPS_64K = QualityItem(quality_id=30216, quality_order=1)
    BPS_132K = QualityItem(quality_id=30232, quality_order=2)
    BPS_192K = QualityItem(quality_id=30280, quality_order=3)
    BPS_DOLBY = QualityItem(quality_id=30250, quality_order=4)
    BPS_HIRES = QualityItem(quality_id=30251, quality_order=5)


CHUNK_SIZE: int = int(1024 * 1024)


MIME_TYPE_VIDEO_MP4 = 'video/mp4'
