"""
Constants
"""
from enum import IntEnum


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
