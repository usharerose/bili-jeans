"""
Utilities for unit test and functional test
"""
from typing import cast, List, Optional

from aiohttp.client import _RequestContextManager
from multidict import CIMultiDictProxy


class MockAsyncResponse(object):

    def __init__(
        self,
        status_code: int,
        content: bytes,
        headers: Optional[CIMultiDictProxy] = None
    ) -> None:
        self._status_code = status_code
        self._content = content
        self._headers = headers

    async def read(self) -> bytes:
        return self._content

    async def __aexit__(self, exc_type, exc, tb) -> None:
        pass

    async def __aenter__(self) -> 'MockAsyncResponse':
        return self

    @property
    def headers(self) -> Optional[CIMultiDictProxy]:
        return self._headers


class MockAsyncIterator:

    def __init__(self, chunk_size: int):
        self._data: List[bytes] = [
            b'dummy content'
        ]
        self._index: int = 0
        self._chunk_size = chunk_size

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._index >= len(self._data):
            raise StopAsyncIteration
        result = self._data[self._index]
        self._index += 1
        return result


def get_mock_async_response(
    status_code: int,
    content: bytes,
    headers: Optional[CIMultiDictProxy] = None
) -> _RequestContextManager:
    mock_resp = cast(
        _RequestContextManager,
        MockAsyncResponse(status_code, content, headers)
    )
    return mock_resp


MOCK_SESS_DATA = 'SESSDATA'
