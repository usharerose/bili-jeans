from http import HTTPStatus
import json
from pathlib import Path
from unittest.mock import patch

from bili_jeans.core.constants import BitRateId, FormatNumberValue
from bili_jeans.core.download import create_audio_task
from bili_jeans.core.pages import get_ugc_pages
from bili_jeans.core.proxy import get_ugc_play
from bili_jeans.core.schemes import WebViewMetaData
from tests.utils import get_mock_async_response, MOCK_SESS_DATA


with open('tests/data/ugc_view/ugc_view_BV1X54y1C74U.json', 'r') as fp:
    DATA_VIEW = json.load(fp)
with open('tests/data/ugc_play/ugc_play_BV1X54y1C74U.json', 'r') as fp:
    DATA_PLAY = json.load(fp)
with open('tests/data/ugc_player/ugc_player_BV1X54y1C74U.json', 'r') as fp:
    DATA_PLAYER = json.load(fp)


@patch('bili_jeans.core.proxy.aiohttp.ClientSession.get')
async def test_create_audio_task(mock_get_req):
    mock_get_req.return_value.__aenter__.side_effect = [
        get_mock_async_response(
            HTTPStatus.OK.value,
            json.dumps(
                DATA_VIEW,
                ensure_ascii=False
            ).encode('utf-8')
        ),
        get_mock_async_response(
            HTTPStatus.OK.value,
            json.dumps(
                DATA_PLAY,
                ensure_ascii=False
            ).encode('utf-8')
        )
    ]
    actual_pages = await get_ugc_pages(
        view_meta=WebViewMetaData(bvid='BV1X54y1C74U'),
        sess_data=MOCK_SESS_DATA
    )
    actual_page, *_ = actual_pages

    actual_ugc_play = await get_ugc_play(
        cid=actual_page.cid,
        bvid=actual_page.bvid,
        aid=actual_page.aid,
        fnval=FormatNumberValue.get_dash_full_fnval(),
        sess_data=MOCK_SESS_DATA
    )

    actual_task = create_audio_task(
        actual_page,
        actual_ugc_play,
        Path('/tmp'),
        BitRateId.BPS_192K.value.quality_id
    )
    assert actual_task.url == (
        'https://upos-sz-mirror08c.bilivideo.com/upgcxcode/46/73/239927346/239927346-1-30280.m4s?'
        'e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_'
        'YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_'
        'g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M='
        '&uipk=5&nbs=1&deadline=1737609056&gen=playurlv2&os=08cbv&oi=0'
        '&trid=5682a9ee2f7a4add8617800f9da55cd1u&mid=12363921&platform=pc&og=hw'
        '&upsig=f7a43be4331fe4427f12cd316693669c'
        '&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og&bvc=vod&nettype=0'
        '&orderid=0,3&buvid=&build=0&f=u_0_0&agrr=0&bw=40047&logo=80000000'
    )
    assert actual_task.file == '/tmp/BV1X54y1C74U/239927346.m4a'
