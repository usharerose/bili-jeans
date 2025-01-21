import pytest

from bili_jeans.core.factory import parse_web_view_url


def test_parse_web_view_url_with_bvid_based_ugc_view():
    sample_url = (
        'https://www.bilibili.com/video/BV1tN4y1F79k?'
        'vd_source=eab9f46166d54e0b07ace25e908097ae&'
        'spm_id_from=333.788.videopod.sections'
    )
    actual_metadata = parse_web_view_url(sample_url)

    assert actual_metadata.aid is None
    assert actual_metadata.bvid == 'BV1tN4y1F79k'


def test_parse_web_view_url_with_aid_based_ugc_view():
    sample_url = (
        'https://www.bilibili.com/video/av2271112/?'
        'vd_source=eab9f46166d54e0b07ace25e908097ae'
    )
    actual_metadata = parse_web_view_url(sample_url)

    assert actual_metadata.aid == 2271112
    assert actual_metadata.bvid is None


def test_parse_web_view_url_with_non_url_params():
    params = 'mock_string'
    with pytest.raises(ValueError, match='Invalid Url: mock_string'):
        parse_web_view_url(params)


def test_parse_web_view_url_with_invalid_url_but_contains_path():
    params = '/video/BV1tN4y1F79k'
    actual_metadata = parse_web_view_url(params)

    assert actual_metadata.aid is None
    assert actual_metadata.bvid == 'BV1tN4y1F79k'
