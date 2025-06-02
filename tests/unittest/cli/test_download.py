import json
from unittest.mock import patch, AsyncMock

from bili_jeans.cli.download import run
from bili_jeans.core.schemes import WebViewMetaData
from tests.utils import MockAsyncIterator, MOCK_SESS_DATA


HTML_CONTENT = b'<!DOCTYPE html><html lang="zh-Hans"></html>'
with open('tests/data/ugc_view/ugc_view_BV1X54y1C74U.json', 'r') as fp:
    DATA_VIEW = json.load(fp)
with open('tests/data/ugc_play/ugc_play_BV1X54y1C74U.json', 'r') as fp:
    DATA_PLAY = json.load(fp)
with open('tests/data/ugc_player/ugc_player_BV1X54y1C74U.json', 'r') as fp:
    DATA_PLAYER = json.load(fp)
with open('tests/data/ugc_view/ugc_view_BV13ht2ejE1S.json', 'r') as fp:
    DATA_VIEW_WITH_FLAC = json.load(fp)
with open('tests/data/ugc_play/ugc_play_BV13ht2ejE1S.json', 'r') as fp:
    DATA_PLAY_WITH_FLAC = json.load(fp)
with open('tests/data/ugc_player/ugc_player_BV13ht2ejE1S.json', 'r') as fp:
    DATA_PLAYER_WITH_FLAC = json.load(fp)
with open('tests/data/ugc_view/ugc_view_BV13L4y1K7th.json', 'r') as fp:
    DATA_VIEW_WITH_DOLBY = json.load(fp)
with open('tests/data/ugc_play/ugc_play_BV13L4y1K7th.json', 'r') as fp:
    DATA_PLAY_WITH_DOLBY = json.load(fp)
with open('tests/data/ugc_player/ugc_player_BV13L4y1K7th.json', 'r') as fp:
    DATA_PLAYER_WITH_DOLBY = json.load(fp)
with open('tests/data/ugc_view/ugc_view_BV1Ys421M7YM.json', 'r') as fp:
    DATA_VIEW_UNPURCHASED = json.load(fp)
with open('tests/data/ugc_play/ugc_play_BV1Ys421M7YM.json', 'r') as fp:
    DATA_PLAY_UNPURCHASED = json.load(fp)
with open('tests/data/ugc_player/ugc_player_BV1Ys421M7YM.json', 'r') as fp:
    DATA_PLAYER_UNPURCHASED = json.load(fp)
with open('tests/data/ugc_view/ugc_view_BV1Et4y1r7Eu.json', 'r') as fp:
    DATA_VIEW_WITH_SUBTITLE = json.load(fp)
with open('tests/data/ugc_play/ugc_play_BV1Et4y1r7Eu.json', 'r') as fp:
    DATA_PLAY_WITH_SUBTITLE = json.load(fp)
with open('tests/data/ugc_player/ugc_player_BV1Et4y1r7Eu.json', 'r') as fp:
    DATA_PLAYER_WITH_SUBTITLE = json.load(fp)


@patch('bili_jeans.core.download.download_task.aiofile.async_open')
@patch('bili_jeans.core.download.download_task.Path')
@patch('bili_jeans.core.download.download_task.aiohttp.ClientSession.get')
@patch('bili_jeans.core.proxy.get_ugc_player_response', new_callable=AsyncMock)
@patch('bili_jeans.core.proxy.get_ugc_play_response', new_callable=AsyncMock)
@patch('bili_jeans.core.proxy.get_ugc_view_response', new_callable=AsyncMock)
@patch('bili_jeans.cli.download.parse_web_view_url', new_callable=AsyncMock)
async def test_run(
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

    await run(
        url='https://www.bilibili.com/video/BV1X54y1C74U/?vd_source=eab9f46166d54e0b07ace25e908097ae',
        directory='/tmp',
        skip_mux=True,
        sess_data=MOCK_SESS_DATA
    )

    # download video, audio separately
    assert mock_async_open.return_value.__aenter__.return_value.write.call_count == 2


@patch('bili_jeans.core.download.download_task.aiofile.async_open')
@patch('bili_jeans.core.download.download_task.Path')
@patch('bili_jeans.core.download.download_task.aiohttp.ClientSession.get')
@patch('bili_jeans.core.proxy.get_ugc_player_response', new_callable=AsyncMock)
@patch('bili_jeans.core.proxy.get_ugc_play_response', new_callable=AsyncMock)
@patch('bili_jeans.core.proxy.get_ugc_view_response', new_callable=AsyncMock)
@patch('bili_jeans.cli.download.parse_web_view_url', new_callable=AsyncMock)
async def test_run_with_flac(
    mock_parse_web_view_url,
    mock_get_ugc_view_resp_req,
    mock_get_ugc_play_resp_req,
    mock_get_ugc_player_resp_req,
    mock_get_resource_req,
    mock_file_p,
    mock_async_open
):
    mock_parse_web_view_url.return_value = WebViewMetaData(
        bvid='BV13ht2ejE1S'
    )
    mock_get_ugc_view_resp_req.return_value = DATA_VIEW_WITH_FLAC
    mock_get_ugc_play_resp_req.return_value = DATA_PLAY_WITH_FLAC
    mock_get_ugc_player_resp_req.return_value = DATA_PLAYER_WITH_FLAC
    mock_get_resource_req.return_value.__aenter__.return_value.content.iter_chunked = MockAsyncIterator
    mock_file_p.return_value.parent.return_value.mkdir.return_value = None
    mock_async_open.return_value.__aenter__.return_value.write = AsyncMock()

    await run(
        url='https://www.bilibili.com/video/BV13ht2ejE1S/?vd_source=eab9f46166d54e0b07ace25e908097ae',
        directory='/tmp',
        skip_mux=True,
        sess_data=MOCK_SESS_DATA
    )

    # download video, audio separately
    assert mock_async_open.return_value.__aenter__.return_value.write.call_count == 2


@patch('bili_jeans.core.download.download_task.aiofile.async_open')
@patch('bili_jeans.core.download.download_task.Path')
@patch('bili_jeans.core.download.download_task.aiohttp.ClientSession.get')
@patch('bili_jeans.core.proxy.get_ugc_player_response', new_callable=AsyncMock)
@patch('bili_jeans.core.proxy.get_ugc_play_response', new_callable=AsyncMock)
@patch('bili_jeans.core.proxy.get_ugc_view_response', new_callable=AsyncMock)
@patch('bili_jeans.cli.download.parse_web_view_url', new_callable=AsyncMock)
async def test_run_with_dolby(
    mock_parse_web_view_url,
    mock_get_ugc_view_resp_req,
    mock_get_ugc_play_resp_req,
    mock_get_ugc_player_resp_req,
    mock_get_resource_req,
    mock_file_p,
    mock_async_open
):
    mock_parse_web_view_url.return_value = WebViewMetaData(
        bvid='BV13L4y1K7th'
    )
    mock_get_ugc_view_resp_req.return_value = DATA_VIEW_WITH_DOLBY
    mock_get_ugc_play_resp_req.return_value = DATA_PLAY_WITH_DOLBY
    mock_get_ugc_player_resp_req.return_value = DATA_PLAYER_WITH_DOLBY
    mock_get_resource_req.return_value.__aenter__.return_value.content.iter_chunked = MockAsyncIterator
    mock_file_p.return_value.parent.return_value.mkdir.return_value = None
    mock_async_open.return_value.__aenter__.return_value.write = AsyncMock()

    await run(
        url='https://www.bilibili.com/video/BV13L4y1K7th/?vd_source=eab9f46166d54e0b07ace25e908097ae',
        directory='/tmp',
        skip_mux=True,
        sess_data=MOCK_SESS_DATA
    )

    # download video, audio separately
    assert mock_async_open.return_value.__aenter__.return_value.write.call_count == 2


@patch('bili_jeans.core.download.download_task.aiofile.async_open')
@patch('bili_jeans.core.download.download_task.Path')
@patch('bili_jeans.core.download.download_task.aiohttp.ClientSession.get')
@patch('bili_jeans.core.proxy.get_ugc_player_response', new_callable=AsyncMock)
@patch('bili_jeans.core.proxy.get_ugc_play_response', new_callable=AsyncMock)
@patch('bili_jeans.core.proxy.get_ugc_view_response', new_callable=AsyncMock)
@patch('bili_jeans.cli.download.parse_web_view_url', new_callable=AsyncMock)
async def test_run_with_declared_quality(
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

    await run(
        url='https://www.bilibili.com/video/BV1X54y1C74U/?vd_source=eab9f46166d54e0b07ace25e908097ae',
        directory='/tmp',
        qn=74,
        reverse_qn=True,
        codec_id=7,
        reverse_bit_rate=False,
        skip_mux=True,
        sess_data=MOCK_SESS_DATA
    )

    # download video, audio separately
    assert mock_async_open.return_value.__aenter__.return_value.write.call_count == 2


@patch('bili_jeans.core.download.download_task.aiofile.async_open')
@patch('bili_jeans.core.download.download_task.Path')
@patch('bili_jeans.core.download.download_task.aiohttp.ClientSession.get')
@patch('bili_jeans.core.proxy.get_ugc_player_response', new_callable=AsyncMock)
@patch('bili_jeans.core.proxy.get_ugc_play_response', new_callable=AsyncMock)
@patch('bili_jeans.core.proxy.get_ugc_view_response', new_callable=AsyncMock)
@patch('bili_jeans.cli.download.parse_web_view_url', new_callable=AsyncMock)
async def test_run_for_paid_ugc_without_privilege(
    mock_parse_web_view_url,
    mock_get_ugc_view_resp_req,
    mock_get_ugc_play_resp_req,
    mock_get_ugc_player_resp_req,
    mock_get_resource_req,
    mock_file_p,
    mock_async_open
):
    mock_parse_web_view_url.return_value = WebViewMetaData(
        bvid='BV1Ys421M7YM'
    )
    mock_get_ugc_view_resp_req.return_value = DATA_VIEW_UNPURCHASED
    mock_get_ugc_play_resp_req.return_value = DATA_PLAY_UNPURCHASED
    mock_get_ugc_player_resp_req.return_value = DATA_PLAYER_UNPURCHASED
    mock_get_resource_req.return_value.__aenter__.return_value.content.iter_chunked = MockAsyncIterator
    mock_file_p.return_value.parent.return_value.mkdir.return_value = None
    mock_async_open.return_value.__aenter__.return_value.write = AsyncMock()

    await run(
        url='https://www.bilibili.com/video/BV1Ys421M7YM/?vd_source=eab9f46166d54e0b07ace25e908097ae',
        directory='/tmp',
        qn=74,
        reverse_qn=True,
        codec_id=7,
        reverse_bit_rate=False,
        skip_mux=True,
        sess_data=MOCK_SESS_DATA
    )

    # the resource for preview is in durl instead of dash
    # which has one resource combined with both video and audio
    assert mock_async_open.return_value.__aenter__.return_value.write.call_count == 1


@patch('bili_jeans.core.download.download_task.aiofile.async_open')
@patch('bili_jeans.core.download.download_task.Path')
@patch('bili_jeans.core.download.download_task.aiohttp.ClientSession.get')
@patch('bili_jeans.core.proxy.get_ugc_player_response', new_callable=AsyncMock)
@patch('bili_jeans.core.proxy.get_ugc_play_response', new_callable=AsyncMock)
@patch('bili_jeans.core.proxy.get_ugc_view_response', new_callable=AsyncMock)
@patch('bili_jeans.cli.download.parse_web_view_url', new_callable=AsyncMock)
async def test_run_enable_danmaku(
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

    await run(
        url='https://www.bilibili.com/video/BV1X54y1C74U/?vd_source=eab9f46166d54e0b07ace25e908097ae',
        directory='/tmp',
        enable_danmaku=True,
        skip_mux=True,
        sess_data=MOCK_SESS_DATA
    )

    # download video, audio and danmaku separately
    assert mock_async_open.return_value.__aenter__.return_value.write.call_count == 3


@patch('bili_jeans.core.download.download_task.aiofile.async_open')
@patch('bili_jeans.core.download.download_task.Path')
@patch('bili_jeans.core.download.download_task.aiohttp.ClientSession.get')
@patch('bili_jeans.core.proxy.get_ugc_player_response', new_callable=AsyncMock)
@patch('bili_jeans.core.proxy.get_ugc_play_response', new_callable=AsyncMock)
@patch('bili_jeans.core.proxy.get_ugc_view_response', new_callable=AsyncMock)
@patch('bili_jeans.cli.download.parse_web_view_url', new_callable=AsyncMock)
async def test_run_enable_cover(
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

    await run(
        url='https://www.bilibili.com/video/BV1X54y1C74U/?vd_source=eab9f46166d54e0b07ace25e908097ae',
        directory='/tmp',
        enable_cover=True,
        skip_mux=True,
        sess_data=MOCK_SESS_DATA
    )

    # download video, audio and cover separately
    assert mock_async_open.return_value.__aenter__.return_value.write.call_count == 3


@patch('bili_jeans.core.download.download_task.aiofile.async_open')
@patch('bili_jeans.core.download.download_task.Path')
@patch('bili_jeans.core.download.download_task.convert_to_srt')
@patch('bili_jeans.core.download.download_task.aiohttp.ClientSession.get')
@patch('bili_jeans.core.proxy.get_ugc_player_response', new_callable=AsyncMock)
@patch('bili_jeans.core.proxy.get_ugc_play_response', new_callable=AsyncMock)
@patch('bili_jeans.core.proxy.get_ugc_view_response', new_callable=AsyncMock)
@patch('bili_jeans.cli.download.parse_web_view_url', new_callable=AsyncMock)
async def test_run_with_subtitle(
    mock_parse_web_view_url,
    mock_get_ugc_view_resp_req,
    mock_get_ugc_play_resp_req,
    mock_get_ugc_player_resp_req,
    mock_get_resource_req,
    mock_convert_to_srt,
    mock_file_p,
    mock_async_open
):
    mock_parse_web_view_url.return_value = WebViewMetaData(
        bvid='BV1Et4y1r7Eu'
    )
    mock_get_ugc_view_resp_req.return_value = DATA_VIEW_WITH_SUBTITLE
    mock_get_ugc_play_resp_req.return_value = DATA_PLAY_WITH_SUBTITLE
    mock_get_ugc_player_resp_req.return_value = DATA_PLAYER_WITH_SUBTITLE
    mock_get_resource_req.return_value.__aenter__.return_value.content.iter_chunked = MockAsyncIterator
    mock_convert_to_srt.return_value = b''
    mock_file_p.return_value.parent.return_value.mkdir.return_value = None
    mock_async_open.return_value.__aenter__.return_value.write = AsyncMock()

    await run(
        url='https://www.bilibili.com/video/BV1Et4y1r7Eu/?vd_source=eab9f46166d54e0b07ace25e908097ae',
        directory='/tmp',
        enable_danmaku=True,
        enable_cover=True,
        enable_subtitle=True,
        skip_mux=True,
        sess_data=MOCK_SESS_DATA
    )

    # download video, audio, cover,
    # subtitle (zh-CN and ai-zh) and their SRT format,
    # and danmaku separately
    assert mock_async_open.return_value.__aenter__.return_value.write.call_count == 8
