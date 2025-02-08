from unittest.mock import patch, AsyncMock

from bili_jeans.core.download.download_task import StreamDownloadTask
from tests.utils import MockAsyncIterator


@patch('bili_jeans.core.download.download_task.aiofile.async_open')
@patch('bili_jeans.core.download.download_task.Path')
@patch('bili_jeans.core.download.download_task.aiohttp.ClientSession.get')
async def test_general_download_task_run(mock_get_req, mock_file_p, mock_async_open):

    sample_url = 'https://upos-sz-mirror08c.bilivideo.com/upgcxcode/sample.m4s'
    sample_file = '/tmp/sample.mp4'

    mock_get_req.return_value.__aenter__.return_value.content.iter_chunked = MockAsyncIterator
    mock_file_p.return_value.parent.return_value.mkdir.return_value = None
    mock_async_open.return_value.__aenter__.return_value.write = AsyncMock()
    download_task = StreamDownloadTask(
        url=sample_url,
        file=sample_file
    )
    await download_task.run()

    mock_async_open.return_value.__aenter__.return_value.write.assert_called_once()
