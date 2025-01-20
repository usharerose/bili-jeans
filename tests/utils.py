"""
Utilities for unit test and functional test
"""
from typing import cast

from aiohttp.client import _RequestContextManager


class MockAsyncResponse(object):

    def __init__(self, status_code: int, content: bytes) -> None:
        self._status_code = status_code
        self._content = content

    async def read(self) -> bytes:
        return self._content

    async def __aexit__(self, exc_type, exc, tb) -> None:
        pass

    async def __aenter__(self) -> 'MockAsyncResponse':
        return self


def get_mock_async_response(
    status_code: int,
    content: bytes
) -> _RequestContextManager:
    mock_resp = cast(
        _RequestContextManager,
        MockAsyncResponse(status_code, content)
    )
    return mock_resp
