from http import HTTPStatus
import json
from unittest.mock import patch

import pytest

from bili_jeans.core.pages import get_ugc_pages
from bili_jeans.core.schemes import WebViewMetaData
from tests.utils import get_mock_async_response, MOCK_SESS_DATA


with open('tests/data/ugc_view/ugc_view_BV1X54y1C74U.json', 'r') as fp:
    DATA_VIEW = json.load(fp)
with open('tests/data/ugc_view/ugc_view_BV1UnExisted.json', 'r') as fp:
    DATA_VIEW_NOT_EXISTED = json.load(fp)
with open('tests/data/ugc_view/ugc_view_BV1tN4y1F79k.json', 'r') as fp:
    DATA_VIEW_WITH_SEASON = json.load(fp)
with open('tests/data/ugc_view/ugc_view_BV1wE4m1R7cu.json', 'r') as fp:
    DATA_VIEW_WITH_MULTI_PAGES = json.load(fp)


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_pages(mock_get_req):
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

    assert isinstance(actual_pages, list)
    assert len(actual_pages) == 1

    actual_page, *_ = actual_pages
    assert actual_page.aid == 842089940
    assert actual_page.bvid == 'BV1X54y1C74U'
    assert actual_page.cid == 239927346
    assert actual_page.title == '呼兰：社保'
    assert actual_page.duration == 177


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_pages_with_wrong_resources(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_VIEW_NOT_EXISTED,
            ensure_ascii=False
        ).encode('utf-8')
    )

    with pytest.raises(ValueError, match='请求错误'):
        await get_ugc_pages(
            view_meta=WebViewMetaData(bvid='BV1UnExisted'),
            sess_data=MOCK_SESS_DATA
        )


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_pages_with_multi_pages(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_VIEW_WITH_MULTI_PAGES,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_pages = await get_ugc_pages(
        view_meta=WebViewMetaData(bvid='BV1wE4m1R7cu'),
        sess_data=MOCK_SESS_DATA
    )

    assert isinstance(actual_pages, list)
    assert len(actual_pages) == 2

    *_, actual_page = actual_pages
    assert actual_page.aid == 1256708328
    assert actual_page.bvid == 'BV1wE4m1R7cu'
    assert actual_page.cid == 25681134366
    assert actual_page.title == '下集'
    assert actual_page.duration == 7861


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_pages_with_timeout_error(mock_get_req):
    mock_get_req.side_effect = TimeoutError
    with pytest.raises(TimeoutError):
        await get_ugc_pages(
            view_meta=WebViewMetaData(bvid='BV1X54y1C74U'),
            sess_data=MOCK_SESS_DATA
        )
