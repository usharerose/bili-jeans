from http import HTTPStatus
import json
from pathlib import Path
from unittest.mock import patch

from bili_jeans.core.download import create_danmaku_task
from bili_jeans.core.pages import get_ugc_pages
from bili_jeans.core.schemes import WebViewMetaData
from tests.utils import get_mock_async_response, MOCK_SESS_DATA


with open('tests/data/ugc_view/ugc_view_BV1X54y1C74U.json', 'r') as fp:
    DATA_VIEW = json.load(fp)
with open('tests/data/ugc_play/ugc_play_BV1X54y1C74U.json', 'r') as fp:
    DATA_PLAY = json.load(fp)
with open('tests/data/ugc_player/ugc_player_BV1X54y1C74U.json', 'r') as fp:
    DATA_PLAYER = json.load(fp)


@patch('bili_jeans.core.proxy.aiohttp.ClientSession.get')
async def test_create_danmaku_task(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_VIEW,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_pages = await get_ugc_pages(
        view_meta=WebViewMetaData(bvid='BV1X54y1C74U'),
        sess_data=MOCK_SESS_DATA
    )
    actual_page, *_ = actual_pages

    actual_task = create_danmaku_task(
        actual_page,
        Path('/tmp')
    )
    assert actual_task.url == (
        'https://api.bilibili.com/x/v1/dm/list.so?oid=239927346'
    )
    assert actual_task.file == '/tmp/BV1X54y1C74U/239927346.xml'
