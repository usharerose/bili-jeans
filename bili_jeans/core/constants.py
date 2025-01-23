"""
Constants
"""
from enum import IntEnum
from functools import reduce


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


########################
# Video Quality Number #
########################
class QualityNumber(IntEnum):
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
    P240 = 6
    P360 = 16
    P480 = 32
    P720 = 64
    P720_60 = 74
    P1080 = 80
    PPLUS_1080 = 112
    P1080_60 = 116
    FOUR_K = 120
    HDR = 125
    DOLBY = 126
    EIGHT_K = 127

    @property
    def is_login_required(self) -> bool:
        return self >= self.P720

    @property
    def is_vip_required(self) -> bool:
        return self >= self.PPLUS_1080

    @classmethod
    def from_value(cls, qn: int) -> 'QualityNumber':
        for item in cls:
            if item == qn:
                return item
        raise ValueError(f'Invalid given quality number : {qn}')


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
        if qn == QualityNumber.HDR:
            result = result | cls.HDR
        if qn >= QualityNumber.FOUR_K:
            result = result | cls.FOUR_K
        if is_dolby_audio:
            result = result | cls.DOLBY_AUDIO
        if qn == QualityNumber.DOLBY:
            result = result | cls.DOLBY_VISION
        if qn == QualityNumber.EIGHT_K:
            result = result | cls.EIGHT_K
        return result


############
# Codec Id #
############
class CodecId(IntEnum):
    """
    AVC, which is avc1.64001E, not support 8K
    HEVC, which is hev1.1.6.L120.90
    AV1, which is av01.0.00M.10.0.110.01.01.01.0
    """
    AVC = 7
    HEVC = 12
    AV1 = 13

    @classmethod
    def from_value(cls, codec_id: int) -> 'CodecId':
        for item in cls:
            if item == codec_id:
                return item
        raise ValueError(f'Invalid given codec Id: {codec_id}')
