from http import HTTPStatus
import json
from pathlib import Path
from unittest.mock import patch

from bili_jeans.core.download import create_subtitle_tasks
from bili_jeans.core.pages import get_ugc_pages
from bili_jeans.core.proxy import get_ugc_player
from bili_jeans.core.schemes import WebViewMetaData
from tests.utils import get_mock_async_response, MOCK_SESS_DATA


with open('tests/data/ugc_view/ugc_view_BV1Et4y1r7Eu.json', 'r') as fp:
    DATA_VIEW = json.load(fp)
with open('tests/data/ugc_play/ugc_play_BV1Et4y1r7Eu.json', 'r') as fp:
    DATA_PLAY = json.load(fp)
with open('tests/data/ugc_player/ugc_player_BV1Et4y1r7Eu.json', 'r') as fp:
    DATA_PLAYER = json.load(fp)


@patch('bili_jeans.core.proxy.aiohttp.ClientSession.get')
async def test_create_subtitle_tasks(mock_get_req):
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
                DATA_PLAYER,
                ensure_ascii=False
            ).encode('utf-8')
        )
    ]
    actual_pages = await get_ugc_pages(
        view_meta=WebViewMetaData(bvid='BV1Et4y1r7Eu'),
        sess_data=MOCK_SESS_DATA
    )
    actual_page, *_ = actual_pages

    actual_player = await get_ugc_player(
        cid=actual_page.cid,
        bvid=actual_page.bvid,
        aid=actual_page.aid,
        sess_data=MOCK_SESS_DATA
    )

    (
        actual_zh_raw_task,
        actual_zh_srt_task,
        actual_ai_raw_task,
        actual_ai_srt_task
    ) = create_subtitle_tasks(
        actual_page,
        actual_player,
        Path('/tmp')
    )
    assert actual_zh_raw_task.url == (
        'https://aisubtitle.hdslb.com/bfs/subtitle/65f8c14e646399df8623d080a0cd8a156410faef.json'
        '?auth_key=1738646346-c9665aa3c1f24b818dd4d8c1d346da71-0-07b06cfe11dcdc29ba8bd985dda7b117'
    )
    assert actual_zh_raw_task.file == (
        '/tmp/BV1Et4y1r7Eu/278154209.37633615760719877.json'
    )
    assert actual_zh_srt_task.url == (
        'https://aisubtitle.hdslb.com/bfs/subtitle/65f8c14e646399df8623d080a0cd8a156410faef.json'
        '?auth_key=1738646346-c9665aa3c1f24b818dd4d8c1d346da71-0-07b06cfe11dcdc29ba8bd985dda7b117'
    )
    assert actual_zh_srt_task.file == (
        '/tmp/BV1Et4y1r7Eu/278154209.37633615760719877.srt'
    )
    assert actual_ai_raw_task.url == (
        'https://aisubtitle.hdslb.com/bfs/ai_subtitle/prod'
        '/62851639827815420902e73973c57d94098c1eaca7bbed34f2'
        '?auth_key=1738646346-04e6a46be3da40b7bb37f466f96047e6-0-94200e63852582eeed444daee7793037'
    )
    assert actual_ai_raw_task.file == (
        '/tmp/BV1Et4y1r7Eu/278154209.1062373651225267712.json'
    )
    assert actual_ai_srt_task.url == (
        'https://aisubtitle.hdslb.com/bfs/ai_subtitle/prod'
        '/62851639827815420902e73973c57d94098c1eaca7bbed34f2'
        '?auth_key=1738646346-04e6a46be3da40b7bb37f466f96047e6-0-94200e63852582eeed444daee7793037'
    )
    assert actual_ai_srt_task.file == (
        '/tmp/BV1Et4y1r7Eu/278154209.1062373651225267712.srt'
    )
