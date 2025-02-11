from click.testing import CliRunner
import json
from unittest.mock import patch, AsyncMock

from bili_jeans.cli import cli
from bili_jeans.core.schemes import WebViewMetaData
from tests.utils import MockAsyncIterator


with open('tests/data/ugc_view/ugc_view_BV1X54y1C74U.json', 'r') as fp:
    DATA_VIEW = json.load(fp)
with open('tests/data/ugc_play/ugc_play_BV1X54y1C74U.json', 'r') as fp:
    DATA_PLAY = json.load(fp)
with open('tests/data/ugc_player/ugc_player_BV1X54y1C74U.json', 'r') as fp:
    DATA_PLAYER = json.load(fp)


@patch('bili_jeans.core.download.download_task.aiofile.async_open')
@patch('bili_jeans.core.download.download_task.Path')
@patch('bili_jeans.core.download.download_task.aiohttp.ClientSession.get')
@patch('bili_jeans.core.proxy.get_ugc_player_response', new_callable=AsyncMock)
@patch('bili_jeans.core.proxy.get_ugc_play_response', new_callable=AsyncMock)
@patch('bili_jeans.core.proxy.get_ugc_view_response', new_callable=AsyncMock)
@patch('bili_jeans.app.parse_web_view_url', new_callable=AsyncMock)
def test_download(
    mock_parse_web_view_url,
    mock_get_ugc_view_resp_req,
    mock_get_ugc_play_resp_req,
    mock_get_ugc_player_resp_req,
    mock_get_resource_req,
    mock_file_p,
    mock_async_open
):
    mock_parse_web_view_url.return_value = WebViewMetaData(
        bvid='BV1X54y1C74U'
    )
    mock_get_ugc_view_resp_req.return_value = DATA_VIEW
    mock_get_ugc_play_resp_req.return_value = DATA_PLAY
    mock_get_ugc_player_resp_req.return_value = DATA_PLAYER
    mock_get_resource_req.return_value.__aenter__.return_value.content.iter_chunked = MockAsyncIterator
    mock_file_p.return_value.parent.return_value.mkdir.return_value = None
    mock_async_open.return_value.__aenter__.return_value.write = AsyncMock()

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            'download',
            '--url',
            'https://www.bilibili.com/video/BV1X54y1C74U/?vd_source=eab9f46166d54e0b07ace25e908097ae',
            '--dir-path',
            '/tmp'
        ]
    )

    # download video and audio separately
    assert mock_async_open.return_value.__aenter__.return_value.write.call_count == 2
    assert result.exit_code == 0
