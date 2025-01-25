from http import HTTPStatus
import json
from unittest.mock import patch

import pytest

from bili_jeans.core.constants import FormatNumberValue, QualityNumber
from bili_jeans.core.proxy import get_ugc_play
from tests.utils import get_mock_async_response, MOCK_SESS_DATA


with open('tests/data/ugc_play_BV1X54y1C74U.json', 'r') as fp:
    DATA_PLAY = json.load(fp)
with open('tests/data/ugc_play_BV1UnExisted.json', 'r') as fp:
    DATA_PLAY_NOT_EXISTED = json.load(fp)
with open('tests/data/ugc_play_BV1Ys421M7YM.json', 'r') as fp:
    DATA_PAID_PLAY = json.load(fp)
with open('tests/data/ugc_play_BV13L4y1K7th.json', 'r') as fp:
    DATA_PLAY_WITH_DOLBY_AUDIO = json.load(fp)
with open('tests/data/ugc_play_BV13ht2ejE1S.json', 'r') as fp:
    DATA_PLAY_WITH_HIRES = json.load(fp)


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_play(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_PLAY,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_play(
        cid=239927346,
        bvid='BV1X54y1C74U',
        aid=842089940,
        qn=None,
        fnval=FormatNumberValue.DASH.value,
        fourk=1,
        sess_data='mock_session_data'
    )

    assert actual_dm.code == 0
    assert actual_dm.message == '0'
    assert actual_dm.ttl == 1
    assert actual_dm.data is not None


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_play_with_wrong_resources(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_PLAY_NOT_EXISTED,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_play(
        cid=239927346,
        bvid='BV1UnExisted',
        aid=842089940,
        qn=None,
        fnval=FormatNumberValue.DASH.value,
        fourk=1,
        sess_data=MOCK_SESS_DATA
    )

    assert actual_dm.code == -400
    assert actual_dm.message == '请求错误'
    assert actual_dm.ttl == 1
    assert actual_dm.data is None


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_play_basic_info(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_PLAY,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_play(
        cid=239927346,
        bvid='BV1X54y1C74U',
        aid=842089940,
        qn=None,
        fnval=FormatNumberValue.DASH.value,
        fourk=1,
        sess_data=MOCK_SESS_DATA
    )
    actual_data = actual_dm.data

    assert actual_data.quality == 64
    assert actual_data.dash is not None
    assert actual_data.durl is None
    assert actual_data.support_formats is not None


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_play_dash_basic_info(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_PLAY,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_play(
        cid=239927346,
        bvid='BV1X54y1C74U',
        aid=842089940,
        qn=None,
        fnval=FormatNumberValue.DASH.value,
        fourk=1,
        sess_data=MOCK_SESS_DATA
    )
    actual_dash = actual_dm.data.dash

    assert actual_dash.duration == 177
    assert actual_dash.audio is not None
    assert actual_dash.dolby is not None
    assert actual_dash.flac is None


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_play_dash_audio(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_PLAY,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_play(
        cid=239927346,
        bvid='BV1X54y1C74U',
        aid=842089940,
        qn=None,
        fnval=FormatNumberValue.DASH.value,
        fourk=1,
        sess_data=MOCK_SESS_DATA
    )
    actual_audio = actual_dm.data.dash.audio

    assert isinstance(actual_audio, list)
    assert len(actual_audio) == 3

    sample_actual_audio, *_ = actual_audio

    assert sample_actual_audio.backup_url == [
        (
            'https://upos-sz-mirror08c.bilivideo.com/upgcxcode/46/73/239927346/239927346-1-30280.m4s?'
            'e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_'
            'YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_'
            'g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&'
            'uipk=5&nbs=1&deadline=1737609056&gen=playurlv2&'
            'os=08cbv&oi=0&trid=5682a9ee2f7a4add8617800f9da55cd1u&mid=12363921&'
            'platform=pc&og=hw&upsig=f7a43be4331fe4427f12cd316693669c&'
            'uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og&'
            'bvc=vod&nettype=0&orderid=1,3&buvid=&build=0&f=u_0_0&agrr=0&bw=40047&logo=40000000'
        ),
        (
            'https://upos-sz-mirror08c.bilivideo.com/upgcxcode/46/73/239927346/239927346-1-30280.m4s?'
            'e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_'
            'YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_'
            'g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&'
            'uipk=5&nbs=1&deadline=1737609056&gen=playurlv2&'
            'os=08cbv&oi=0&trid=5682a9ee2f7a4add8617800f9da55cd1u&mid=12363921&'
            'platform=pc&og=hw&upsig=f7a43be4331fe4427f12cd316693669c&'
            'uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og&'
            'bvc=vod&nettype=0&orderid=2,3&buvid=&build=0&f=u_0_0&agrr=0&bw=40047&logo=40000000'
        )
    ]
    assert sample_actual_audio.bandwidth == 319181
    assert sample_actual_audio.base_url == (
        'https://upos-sz-mirror08c.bilivideo.com/upgcxcode/46/73/239927346/239927346-1-30280.m4s?'
        'e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_'
        'YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_'
        'g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&'
        'uipk=5&nbs=1&deadline=1737609056&gen=playurlv2&'
        'os=08cbv&oi=0&trid=5682a9ee2f7a4add8617800f9da55cd1u&mid=12363921&'
        'platform=pc&og=hw&upsig=f7a43be4331fe4427f12cd316693669c&'
        'uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og&'
        'bvc=vod&nettype=0&orderid=0,3&buvid=&build=0&f=u_0_0&agrr=0&bw=40047&logo=80000000'
    )

    assert sample_actual_audio.codecid == 0
    assert sample_actual_audio.codecs == 'mp4a.40.2'
    assert sample_actual_audio.height == 0
    assert sample_actual_audio.id_field == 30280
    assert sample_actual_audio.mime_type == 'audio/mp4'
    assert sample_actual_audio.width == 0


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_play_dash_without_dolby_audio(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_PLAY,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_play(
        cid=239927346,
        bvid='BV1X54y1C74U',
        aid=842089940,
        qn=None,
        fnval=FormatNumberValue.DASH.value,
        fourk=1,
        sess_data=MOCK_SESS_DATA
    )
    actual_dolby = actual_dm.data.dash.dolby

    assert actual_dolby.type_field == 0
    assert actual_dolby.audio is None


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_play_dash_with_dolby_audio(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_PLAY_WITH_DOLBY_AUDIO,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_play(
        cid=733892245,
        bvid='BV13L4y1K7th',
        qn=None,
        fnval=FormatNumberValue.get_dash_full_fnval(),
        fourk=1,
        sess_data=MOCK_SESS_DATA
    )
    actual_dolby = actual_dm.data.dash.dolby

    assert actual_dolby.type_field == 2
    assert isinstance(actual_dolby.audio, list)
    assert len(actual_dolby.audio) == 1

    sample_actual_audio, *_ = actual_dolby.audio
    assert sample_actual_audio.backup_url == [
        (
            'https://upos-sz-mirror08c.bilivideo.com/upgcxcode/45/22/733892245/733892245-1-30250.m4s?'
            'e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_'
            'YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_'
            'g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&'
            'uipk=5&nbs=1&deadline=1737610703&gen=playurlv2&'
            'os=08cbv&oi=0&trid=858ca76e132d4a6e8d5c46296f9d9b1fu&mid=12363921&'
            'platform=pc&og=hw&upsig=efa817d394341f8e59be29996273694a&'
            'uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og&'
            'bvc=vod&nettype=0&orderid=1,3&buvid=&build=0&f=u_0_0&agrr=0&bw=56526&logo=40000000'
        ),
        (
            'https://upos-sz-mirror08c.bilivideo.com/upgcxcode/45/22/733892245/733892245-1-30250.m4s?'
            'e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_'
            'YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_'
            'g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&'
            'uipk=5&nbs=1&deadline=1737610703&gen=playurlv2&'
            'os=08cbv&oi=0&trid=858ca76e132d4a6e8d5c46296f9d9b1fu&mid=12363921&'
            'platform=pc&og=hw&upsig=efa817d394341f8e59be29996273694a&'
            'uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og&'
            'bvc=vod&nettype=0&orderid=2,3&buvid=&build=0&f=u_0_0&agrr=0&bw=56526&logo=40000000'
        )
    ]
    assert sample_actual_audio.bandwidth == 448230
    assert sample_actual_audio.base_url == (
        'https://cn-tj-cu-01-12.bilivideo.com/upgcxcode/45/22/733892245/733892245-1-30250.m4s?'
        'e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_'
        'YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_'
        'g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&'
        'uipk=5&nbs=1&deadline=1737610703&gen=playurlv2&'
        'os=bcache&oi=0&trid=0000858ca76e132d4a6e8d5c46296f9d9b1fu&mid=12363921&'
        'platform=pc&og=hw&upsig=4cf3ceab0a3b98524d9b20c21eab38f8&'
        'uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og&cdnid=87212&'
        'bvc=vod&nettype=0&orderid=0,3&buvid=&build=0&f=u_0_0&agrr=0&bw=56526&logo=80000000'
    )
    assert sample_actual_audio.codecid == 0
    assert sample_actual_audio.codecs == 'ec-3'
    assert sample_actual_audio.height == 0
    assert sample_actual_audio.id_field == 30250
    assert sample_actual_audio.mime_type == 'audio/mp4'
    assert sample_actual_audio.width == 0


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_play_dash_with_hires(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_PLAY_WITH_HIRES,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_play(
        cid=25954616353,
        bvid='BV13ht2ejE1S',
        qn=None,
        fnval=FormatNumberValue.get_dash_full_fnval(),
        fourk=1,
        sess_data=MOCK_SESS_DATA
    )
    actual_flac = actual_dm.data.dash.flac

    assert actual_flac.display is True

    actual_audio = actual_flac.audio
    assert actual_audio.backup_url == [
        (
            'https://upos-sz-estgoss.bilivideo.com/upgcxcode/53/63/25954616353/25954616353-1-30251.m4s?'
            'e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_'
            'YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_'
            'g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&'
            'uipk=5&nbs=1&deadline=1737611518&gen=playurlv2&'
            'os=upos&oi=0&trid=546f2a4166934751a419e9636b430280u&mid=12363921&'
            'platform=pc&og=cos&upsig=75d6d084a6d04239709bc2a0f43b06c5&'
            'uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og&'
            'bvc=vod&nettype=0&orderid=1,3&buvid=&build=0&f=u_0_0&agrr=0&bw=199130&logo=40000000'
        ),
        (
            'https://upos-sz-estgoss.bilivideo.com/upgcxcode/53/63/25954616353/25954616353-1-30251.m4s?'
            'e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_'
            'YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_'
            'g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&'
            'uipk=5&nbs=1&deadline=1737611518&gen=playurlv2&'
            'os=upos&oi=0&trid=546f2a4166934751a419e9636b430280u&mid=12363921&'
            'platform=pc&og=cos&upsig=75d6d084a6d04239709bc2a0f43b06c5&'
            'uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og&'
            'bvc=vod&nettype=0&orderid=2,3&buvid=&build=0&f=u_0_0&agrr=0&bw=199130&logo=40000000'
        )
    ]
    assert actual_audio.bandwidth == 1592578
    assert actual_audio.base_url == (
        'https://xy116x207x155x154xy240ey95dy1010y700yy84xy.mcdn.bilivideo.cn:4483/'
        'upgcxcode/53/63/25954616353/25954616353-1-30251.m4s?'
        'e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_'
        'YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_'
        'g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&'
        'uipk=5&nbs=1&deadline=1737611518&gen=playurlv2&'
        'os=mcdn&oi=0&trid=0000546f2a4166934751a419e9636b430280u&mid=12363921&'
        'platform=pc&og=cos&upsig=faecdaa20c6daf148a1c72d1bcb2e99b&'
        'uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og&mcdnid=50017681&'
        'bvc=vod&nettype=0&orderid=0,3&buvid=&build=0&f=u_0_0&agrr=0&bw=199130&logo=A0020000'
    )
    assert actual_audio.codecid == 0
    assert actual_audio.codecs == 'fLaC'
    assert actual_audio.height == 0
    assert actual_audio.id_field == 30251
    assert actual_audio.mime_type == 'audio/mp4'
    assert actual_audio.width == 0


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_play_dash_video(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_PLAY,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_play(
        cid=239927346,
        bvid='BV1X54y1C74U',
        aid=842089940,
        qn=None,
        fnval=FormatNumberValue.DASH.value,
        fourk=1,
        sess_data=MOCK_SESS_DATA
    )
    actual_video = actual_dm.data.dash.video

    assert isinstance(actual_video, list)
    assert len(actual_video) == 10

    sample_actual_video, *_ = actual_video

    assert sample_actual_video.backup_url == [
        (
            'https://upos-sz-mirror08c.bilivideo.com/upgcxcode/46/73/239927346/239927346-1-30112.m4s?'
            'e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_'
            'YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_'
            'g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&'
            'uipk=5&nbs=1&deadline=1737609056&gen=playurlv2&'
            'os=08cbv&oi=0&trid=5682a9ee2f7a4add8617800f9da55cd1u&mid=12363921&'
            'platform=pc&og=hw&upsig=89771385d769e597dd788d62aa981cee&'
            'uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og&'
            'bvc=vod&nettype=0&orderid=1,3&buvid=&build=0&f=u_0_0&agrr=0&bw=420479&logo=40000000'
        ),
        (
            'https://upos-sz-mirror08c.bilivideo.com/upgcxcode/46/73/239927346/239927346-1-30112.m4s?'
            'e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_'
            'YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_'
            'g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&'
            'uipk=5&nbs=1&deadline=1737609056&gen=playurlv2&'
            'os=08cbv&oi=0&trid=5682a9ee2f7a4add8617800f9da55cd1u&mid=12363921&'
            'platform=pc&og=hw&upsig=89771385d769e597dd788d62aa981cee&'
            'uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og&'
            'bvc=vod&nettype=0&orderid=2,3&buvid=&build=0&f=u_0_0&agrr=0&bw=420479&logo=40000000'
        )
    ]
    assert sample_actual_video.bandwidth == 3352406
    assert sample_actual_video.base_url == (
        'https://upos-sz-mirror08c.bilivideo.com/upgcxcode/46/73/239927346/239927346-1-30112.m4s?'
        'e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_'
        'YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_'
        'g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&'
        'uipk=5&nbs=1&deadline=1737609056&gen=playurlv2&'
        'os=08cbv&oi=0&trid=5682a9ee2f7a4add8617800f9da55cd1u&mid=12363921&'
        'platform=pc&og=hw&upsig=89771385d769e597dd788d62aa981cee&'
        'uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og&'
        'bvc=vod&nettype=0&orderid=0,3&buvid=&build=0&f=u_0_0&agrr=0&bw=420479&logo=80000000'
    )
    assert sample_actual_video.codecid == 7
    assert sample_actual_video.codecs == 'avc1.640032'
    assert sample_actual_video.height == 1080
    assert sample_actual_video.id_field == 112
    assert sample_actual_video.mime_type == 'video/mp4'
    assert sample_actual_video.width == 1920


@patch('aiohttp.ClientSession.get')
async def test_get_paid_ugc_play_without_privilege(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_PAID_PLAY,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_play(
        cid=1566548814,
        bvid='BV1Ys421M7YM',
        aid=1855474163,
        qn=None,
        fnval=FormatNumberValue.DASH.value,
        fourk=1
    )
    actual_data = actual_dm.data

    assert actual_data.quality == 32
    assert actual_data.dash is None
    assert actual_data.durl is not None
    assert actual_data.support_formats is not None


@patch('aiohttp.ClientSession.get')
async def test_get_paid_ugc_play_durl(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_PAID_PLAY,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_play(
        cid=1566548814,
        bvid='BV1Ys421M7YM',
        aid=1855474163,
        qn=None,
        fnval=FormatNumberValue.DASH.value,
        fourk=1
    )
    actual_durl = actual_dm.data.durl

    assert isinstance(actual_durl, list)
    assert len(actual_durl) == 1

    sample_actual_durl, *_ = actual_durl
    assert sample_actual_durl.length == 1050160
    assert sample_actual_durl.order == 1
    assert sample_actual_durl.size == 60154454
    assert sample_actual_durl.url == (
        'https://xy120x209x212x6xy2409y8730ye0efy10yy20xy.mcdn.bilivideo.cn:4483/'
        'upgcxcode/14/88/1566548814/1566548814_u1-1-29.mp4?'
        'e=ig8euxZM2rNcNbRVhwdVhwdlhWdVhwdVhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_'
        'YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_'
        'g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&'
        'uipk=5&nbs=1&deadline=1737616642&gen=playurlv2&'
        'os=mcdn&oi=0&trid=0000ec1a95a2a70345d0838d6ab96b1ed47eu&mid=0&'
        'platform=pc&og=cos&upsig=2fdc0b1baebb194ac3de41090d75060d&'
        'uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og&mcdnid=50016813&'
        'bvc=vod&nettype=0&orderid=0,3&buvid=&build=0&f=u_0_0&agrr=0&bw=57289&logo=A0020000'
    )
    assert sample_actual_durl.backup_url == [
        (
            'https://upos-sz-mirrorcos.bilivideo.com/upgcxcode/14/88/1566548814/1566548814_u1-1-29.mp4?'
            'e=ig8euxZM2rNcNbRVhwdVhwdlhWdVhwdVhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_'
            'YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_'
            'g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&'
            'uipk=5&nbs=1&deadline=1737616642&gen=playurlv2&'
            'os=cosbv&oi=0&trid=ec1a95a2a70345d0838d6ab96b1ed47eu&mid=0&'
            'platform=pc&og=cos&upsig=6043548050387bf62e4ad78e0270fec0&'
            'uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og&'
            'bvc=vod&nettype=0&orderid=1,3&buvid=&build=0&f=u_0_0&agrr=0&bw=57289&logo=40000000'
        ),
        (
            'https://upos-sz-mirrorcos.bilivideo.com/upgcxcode/14/88/1566548814/1566548814_u1-1-29.mp4?'
            'e=ig8euxZM2rNcNbRVhwdVhwdlhWdVhwdVhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_'
            'YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_'
            'g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&'
            'uipk=5&nbs=1&deadline=1737616642&gen=playurlv2&'
            'os=cosbv&oi=0&trid=ec1a95a2a70345d0838d6ab96b1ed47eu&mid=0&'
            'platform=pc&og=cos&upsig=6043548050387bf62e4ad78e0270fec0&'
            'uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og&'
            'bvc=vod&nettype=0&orderid=2,3&buvid=&build=0&f=u_0_0&agrr=0&bw=57289&logo=40000000'
        )
    ]


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_play_support_formats(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_PLAY,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_play(
        cid=239927346,
        bvid='BV1X54y1C74U',
        aid=842089940,
        qn=None,
        fnval=FormatNumberValue.DASH.value,
        fourk=1,
        sess_data=MOCK_SESS_DATA
    )
    actual_support_formats = actual_dm.data.support_formats

    assert isinstance(actual_support_formats, list)
    assert len(actual_support_formats) == 5

    sample_actual_support_format, *_ = actual_support_formats
    assert sample_actual_support_format.codecs == [
        'avc1.640032',
        'hev1.1.6.L150.90'
    ]
    assert sample_actual_support_format.display_desc == '1080P'
    assert sample_actual_support_format.format_field == 'hdflv2'
    assert sample_actual_support_format.new_description == '1080P 高码率'
    assert sample_actual_support_format.quality == 112


@patch('aiohttp.ClientSession.get')
async def test_get_ugc_play_by_aid(mock_get_req):
    mock_get_req.return_value.__aenter__.return_value = get_mock_async_response(
        HTTPStatus.OK.value,
        json.dumps(
            DATA_PLAY,
            ensure_ascii=False
        ).encode('utf-8')
    )
    actual_dm = await get_ugc_play(
        cid=239927346,
        aid=842089940,
        qn=QualityNumber.PPLUS_1080.quality_id,
        fnval=FormatNumberValue.DASH.value,
        fourk=1,
        sess_data=MOCK_SESS_DATA
    )
    actual_data = actual_dm.data

    assert actual_data is not None


async def test_get_ugc_play_without_bv_or_av_id():
    with pytest.raises(ValueError):
        await get_ugc_play(
            cid=239927346,
            qn=None,
            fnval=FormatNumberValue.DASH.value,
            fourk=1
        )
