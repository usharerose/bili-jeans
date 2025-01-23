from asyncio import TimeoutError
from http import HTTPStatus
import json
from unittest.mock import patch

import pytest

from bili_jeans.core.proxy import get_ugc_view
from tests.utils import get_mock_async_response, MOCK_SESS_DATA


with open('tests/data/ugc_view_BV1X54y1C74U.json', 'r') as fp:
    DATA_VIEW = json.load(fp)
with open('tests/data/ugc_view_BVNotExisted.json', 'r') as fp:
    DATA_VIEW_NOT_EXISTED = json.load(fp)
with open('tests/data/ugc_view_BV1tN4y1F79k.json', 'r') as fp:
    DATA_VIEW_WITH_SEASON = json.load(fp)


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_view(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_VIEW,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_view(
        bvid='BV1X54y1C74U',
        sess_data=MOCK_SESS_DATA
    )

    assert actual_dm.code == 0
    assert actual_dm.message == '0'
    assert actual_dm.ttl == 1
    assert actual_dm.data is not None


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_view_with_wrong_resources(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_VIEW_NOT_EXISTED,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_view(bvid='BVNotExisted')

    assert actual_dm.code == -400
    assert actual_dm.message == '请求错误'
    assert actual_dm.ttl == 1
    assert actual_dm.data is None


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_view_basic_info(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_VIEW,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_view(bvid='BV1X54y1C74U')
    actual_data = actual_dm.data

    assert actual_data.aid == 842089940
    assert actual_data.bvid == 'BV1X54y1C74U'
    assert actual_data.cid == 239927346
    assert actual_data.ctime == 1599717912
    assert actual_data.desc == '-'
    assert actual_data.duration == 177
    assert (
        actual_data.pic ==
        'http://i0.hdslb.com/bfs/archive/637b892a9d16daf7220071e4a2090533e3782922.jpg'
    )
    assert actual_data.pubdate == 1599717911
    assert actual_data.title == '【脱口秀大会】呼兰：社保维系了我的脱口秀梦想...'


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_view_without_season(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_VIEW,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_view(bvid='BV1X54y1C74U')
    actual_data = actual_dm.data

    assert actual_data.is_season_display is False
    assert actual_data.ugc_season is None


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_view_owner(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_VIEW,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_view(bvid='BV1X54y1C74U')
    actual_owner = actual_dm.data.owner

    assert (
        actual_owner.face ==
        'http://i2.hdslb.com/bfs/face/7bcb54931eb26e29cd75bc8059dd74647fcfe2c3.jpg'
    )
    assert actual_owner.mid == 158647239
    assert actual_owner.name == '呼兰hooligan'


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_view_pages(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_VIEW,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_view(bvid='BV1X54y1C74U')
    actual_pages = actual_dm.data.pages

    assert isinstance(actual_pages, list)
    assert len(actual_pages) == 1

    sample_actual_page, *_ = actual_pages
    assert sample_actual_page.cid == 239927346
    assert sample_actual_page.duration == 177
    assert sample_actual_page.page == 1
    assert sample_actual_page.part == '呼兰：社保'


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_view_with_ugc_season(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_VIEW_WITH_SEASON,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_view(bvid='BV1tN4y1F79k')
    actual_data = actual_dm.data

    assert actual_data.is_season_display is True
    assert actual_data.ugc_season is not None


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_view_ugc_season_basic_info(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_VIEW_WITH_SEASON,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_view(bvid='BV1tN4y1F79k')
    actual_ugc_season = actual_dm.data.ugc_season

    assert (
        actual_ugc_season.cover ==
        'https://archive.biliimg.com/bfs/archive/5484d44e54cc934fd066ccc2f313752fa8fcb77b.jpg'
    )
    assert actual_ugc_season.ep_count == 2
    assert actual_ugc_season.id_field == 650336
    expected_ugc_season_intro = (
        '有人不入爱河，有人深陷欲网。\\n'
        '有人阴阳两隔，有人各天一方。\\n'
        '最渴望取的，未必是真经，或许是真情。\\n'
        '有道是——\\n'
        '易求无价宝，难得有心郎。\\n'
        '\\n'
        '由游戏科学开发的西游题材单机·动作·角色扮演游戏《黑神话：悟空》今日正式公布了一段新的6分钟实机剧情片段，所有出场角色均为首次亮相。\\n'
        '\\n'
        'P1：正片\\n'
        'P2：插曲纯享版\\n'
        '\\n'
        '视频插曲及伴奏已同步上传网易云音乐，QQ音乐。搜索“黑神话”或“戒网”即可收听。\\n'
        '\\n'
        '更多信息可关注我们的微博@黑神话之悟空 或前往官网>>heishenhua.com'
    )
    assert actual_ugc_season.intro == expected_ugc_season_intro
    assert actual_ugc_season.mid == 642389251
    assert actual_ugc_season.title == '《黑神话：悟空》6分钟实机剧情片段'


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_view_section_basic_info(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_VIEW_WITH_SEASON,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_view(bvid='BV1tN4y1F79k')
    actual_ugc_sections = actual_dm.data.ugc_season.sections

    assert isinstance(actual_ugc_sections, list)
    assert len(actual_ugc_sections) == 1

    sample_actual_section, *_ = actual_ugc_sections
    assert sample_actual_section.id_field == 752877
    assert sample_actual_section.season_id == 650336
    assert sample_actual_section.title == '正片'


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_view_episode_basic_info(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_VIEW_WITH_SEASON,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_view(bvid='BV1tN4y1F79k')
    actual_section, *_ = actual_dm.data.ugc_season.sections
    actual_episodes = actual_section.episodes

    assert isinstance(actual_episodes, list)
    assert len(actual_episodes) == 2

    sample_actual_episode, *_ = actual_episodes
    assert sample_actual_episode.aid == 899743670
    assert sample_actual_episode.bvid == 'BV1tN4y1F79k'
    assert sample_actual_episode.cid == 808240617
    assert sample_actual_episode.id_field == 10399725
    assert sample_actual_episode.season_id == 650336
    assert sample_actual_episode.section_id == 752877
    assert sample_actual_episode.title == '《黑神话：悟空》6分钟实机剧情片段'


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_view_episode_arc(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_VIEW_WITH_SEASON,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_view(bvid='BV1tN4y1F79k')
    actual_section, *_ = actual_dm.data.ugc_season.sections
    actual_episode, *_ = actual_section.episodes
    actual_arc = actual_episode.arc

    assert actual_arc.aid == 899743670
    assert actual_arc.ctime == 1660960800
    assert actual_arc.desc == ''
    assert actual_arc.duration == 381
    assert actual_arc.pic == 'http://i0.hdslb.com/bfs/archive/5484d44e54cc934fd066ccc2f313752fa8fcb77b.jpg'
    assert actual_arc.pubdate == 1660960800
    assert actual_arc.title == '《黑神话：悟空》6分钟实机剧情片段'


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_view_episode_page(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_VIEW_WITH_SEASON,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_view(bvid='BV1tN4y1F79k')
    actual_section, *_ = actual_dm.data.ugc_season.sections
    actual_episode, *_ = actual_section.episodes
    actual_page = actual_episode.page

    assert actual_page.cid == 808240617
    assert actual_page.duration == 381
    assert actual_page.page == 1
    assert actual_page.part == '《黑神话：悟空》6分钟实机剧情片段'


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_view_episode_pages(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_VIEW_WITH_SEASON,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_view(bvid='BV1tN4y1F79k')
    actual_section, *_ = actual_dm.data.ugc_season.sections
    actual_episode, *_ = actual_section.episodes
    actual_pages = actual_episode.pages

    assert isinstance(actual_pages, list)
    assert len(actual_pages) == 1

    actual_page, *_ = actual_pages
    assert actual_page.cid == 808240617
    assert actual_page.duration == 381
    assert actual_page.page == 1
    assert actual_page.part == '《黑神话：悟空》6分钟实机剧情片段'


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_view_with_connection_error(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_VIEW_WITH_SEASON,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_view(bvid='BV1tN4y1F79k')
    actual_section, *_ = actual_dm.data.ugc_season.sections
    actual_episode, *_ = actual_section.episodes
    actual_pages = actual_episode.pages

    assert isinstance(actual_pages, list)
    assert len(actual_pages) == 1

    actual_page, *_ = actual_pages
    assert actual_page.cid == 808240617
    assert actual_page.duration == 381
    assert actual_page.page == 1
    assert actual_page.part == '《黑神话：悟空》6分钟实机剧情片段'


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_view_with_timeout_error(mock_get_req):
    mock_get_req.side_effect = TimeoutError
    with pytest.raises(TimeoutError):
        await get_ugc_view(bvid='BV1X54y1C74U')


async def test_get_ugc_view_without_params():
    with pytest.raises(ValueError):
        await get_ugc_view()


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_view_by_aid(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_VIEW,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_view(aid=842089940)
    actual_data = actual_dm.data

    assert actual_data.aid == 842089940
    assert actual_data.bvid == 'BV1X54y1C74U'
