from http import HTTPStatus
from unittest.mock import patch

from aiohttp import InvalidUrlClientError
from multidict import CIMultiDict, CIMultiDictProxy
import pytest

from bili_jeans.core.factory import parse_web_view_url
from tests.utils import get_mock_async_response


HTML_CONTENT = b'<!DOCTYPE html><html lang="zh-Hans"></html>'


@patch('aiohttp.ClientSession.get')
async def test_parse_web_view_url_with_bvid_based_ugc_view(mock_get_req):
    sample_url = (
        'https://www.bilibili.com/video/BV1tN4y1F79k?'
        'vd_source=eab9f46166d54e0b07ace25e908097ae&'
        'spm_id_from=333.788.videopod.sections'
    )
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        HTML_CONTENT,
        CIMultiDictProxy(
            CIMultiDict(
                location=(
                    '/video/BV1tN4y1F79k?'
                    'vd_source=eab9f46166d54e0b07ace25e908097ae&'
                    'spm_id_from=333.788.videopod.sections'
                )
            )
        )
    )
    actual_metadata = await parse_web_view_url(sample_url)

    assert actual_metadata.aid is None
    assert actual_metadata.bvid == 'BV1tN4y1F79k'


@patch('aiohttp.ClientSession.get')
async def test_parse_web_view_url_with_aid_based_ugc_view(mock_get_req):
    sample_url = (
        'https://www.bilibili.com/video/av2271112/?'
        'vd_source=eab9f46166d54e0b07ace25e908097ae'
    )
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        HTML_CONTENT,
        CIMultiDictProxy(CIMultiDict())
    )
    actual_metadata = await parse_web_view_url(sample_url)

    assert actual_metadata.aid == 2271112
    assert actual_metadata.bvid is None


@patch('aiohttp.ClientSession.get')
async def test_parse_web_view_url_with_non_url_params(mock_get_req):
    params = 'mock_string'
    mock_get_req.side_effect = InvalidUrlClientError(params)
    with pytest.raises(
        ValueError,
        match=f'Invalid Url. source Url: {params}, destination Url: {params}'
    ):
        await parse_web_view_url(params)


@patch('aiohttp.ClientSession.get')
async def test_parse_web_view_url_with_invalid_url_but_contains_path(mock_get_req):
    params = '/video/BV1tN4y1F79k'
    mock_get_req.side_effect = InvalidUrlClientError(params)
    actual_metadata = await parse_web_view_url(params)

    assert actual_metadata.aid is None
    assert actual_metadata.bvid == 'BV1tN4y1F79k'


@patch('aiohttp.ClientSession.get')
async def test_parse_web_view_url_of_pgc_resource_with_bvid(mock_get_req):
    """
    PGC resource also has bvid-declared Url
    the metadata should be based on destination Url
    """
    sample_url = 'https://www.bilibili.com/video/BV1tL4y1i7UZ/'
    dest_url = 'https://www.bilibili.com/bangumi/play/ep249470'
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        HTML_CONTENT,
        CIMultiDictProxy(CIMultiDict(location=dest_url))
    )
    with pytest.raises(
        ValueError,
        match=f'Invalid Url. source Url: {sample_url}, destination Url: {dest_url}'
    ):
        await parse_web_view_url(sample_url)


@patch('aiohttp.ClientSession.get')
async def test_parse_web_view_url_of_pgc_resource_with_aid(mock_get_req):
    """
    PGC resource also has aid-declared Url
    the metadata should be based on destination Url
    """
    sample_url = 'https://www.bilibili.com/video/av31703892/'
    dest_url = 'https://www.bilibili.com/bangumi/play/ep249469'
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        HTML_CONTENT,
        CIMultiDictProxy(CIMultiDict(location=dest_url))
    )
    with pytest.raises(
        ValueError,
        match=f'Invalid Url. source Url: {sample_url}, destination Url: {dest_url}'
    ):
        await parse_web_view_url(sample_url)
