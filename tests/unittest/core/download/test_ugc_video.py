from http import HTTPStatus
import json
from pathlib import Path
from unittest.mock import patch

from bili_jeans.core.constants import FormatNumberValue
from bili_jeans.core.download import create_video_task
from bili_jeans.core.pages import get_ugc_pages
from bili_jeans.core.proxy import get_ugc_play
from bili_jeans.core.schemes import WebViewMetaData
from tests.utils import get_mock_async_response, MOCK_SESS_DATA


with open('tests/data/ugc_view/ugc_view_BV1Et4y1r7Eu.json', 'r') as fp:
    DATA_VIEW = json.load(fp)
with open('tests/data/ugc_play/ugc_play_BV1Et4y1r7Eu.json', 'r') as fp:
    DATA_PLAY = json.load(fp)
with open('tests/data/ugc_player/ugc_player_BV1Et4y1r7Eu.json', 'r') as fp:
    DATA_PLAYER = json.load(fp)


@patch('bili_jeans.core.proxy.aiohttp.ClientSession.get')
async def test_create_video_task(mock_get_req):
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
        view_meta=WebViewMetaData(bvid='BV1Et4y1r7Eu'),
        sess_data=MOCK_SESS_DATA
    )
    actual_page, *_ = actual_pages

    actual_play = await get_ugc_play(
        cid=actual_page.cid,
        bvid=actual_page.bvid,
        aid=actual_page.aid,
        fnval=FormatNumberValue.get_dash_full_fnval(),
        sess_data=MOCK_SESS_DATA
    )

    actual_task = create_video_task(
        actual_page,
        actual_play,
        Path('/tmp')
    )
    assert actual_task.url == (
        'https://xy36x163x204x18xy2409y8770y24f0y2yy18xy.mcdn.bilivideo.cn:4483'
        '/upgcxcode/09/42/278154209/278154209_nb2-1-30016.m4s?'
        'e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_'
        'YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_'
        'g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M='
        '&uipk=5&nbs=1&deadline=1738653104&gen=playurlv2&os=mcdn&oi=0'
        '&trid=00005bb76121b1ae4e39a74ea61005bdf06du&mid=12363921'
        '&platform=pc&og=cos&upsig=adfe5a866c9c9e58a289132210a6a633'
        '&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og'
        '&mcdnid=50015208&bvc=vod&nettype=0&orderid=0,3&buvid=&build=0'
        '&f=u_0_0&agrr=0&bw=19675&logo=A0020000'
    )
    assert actual_task.file == '/tmp/BV1Et4y1r7Eu/278154209.mp4'
