from unittest.mock import patch, AsyncMock

from bili_jeans.core.download import download_resource
from tests.utils import MockAsyncIterator


@patch('aiofile.async_open')
@patch('aiohttp.ClientSession.get')
async def test_download_resource(mock_get_req, mock_async_open):

    sample_url = 'https://upos-sz-mirror08c.bilivideo.com/upgcxcode/sample.m4s'
    sample_file = '/tmp/sample.mp4'

    mock_get_req.return_value.__aenter__.return_value.content.iter_chunked = MockAsyncIterator
    mock_async_open.return_value.__aenter__.return_value.write = AsyncMock()
    await download_resource(sample_url, sample_file)

    mock_async_open.return_value.__aenter__.return_value.write.assert_called_once()
