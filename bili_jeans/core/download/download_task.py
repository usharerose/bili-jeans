"""
Download resources to local
"""
from abc import ABC, abstractmethod
from pathlib import Path

import aiofile
import aiohttp

from ..constants import CHUNK_SIZE, HEADERS
from ..utils import convert_to_srt


class BaseCoroutineDownloadTask(ABC):

    def __init__(
        self,
        url: str,
        file: str,
        is_stream: bool = True
    ) -> None:
        self._url = url
        self._file = file
        self._file_p = Path(file)
        self._is_stream = is_stream

    async def run(self) -> None:
        if self._is_stream:
            await self.download_stream()
        else:
            await self.download()

    async def download(self) -> None:
        content = await self._request()
        content = self.post_process_content(content)
        self._file_p.parent.mkdir(parents=True, exist_ok=True)
        async with aiofile.async_open(self._file, 'wb') as afp:
            await afp.write(content)

    async def download_stream(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self._url,
                headers=HEADERS
            ) as resp:
                self._file_p.parent.mkdir(parents=True, exist_ok=True)

                async with aiofile.async_open(self._file, 'wb') as afp:
                    async for chunk_data in resp.content.iter_chunked(CHUNK_SIZE):
                        await afp.write(chunk_data)  # type: ignore[attr-defined]

    async def _request(self) -> bytes:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self._url,
                headers=HEADERS
            ) as resp:
                return await resp.read()

    @abstractmethod
    def post_process_content(self, content: bytes) -> bytes:
        pass


class StreamDownloadTask(BaseCoroutineDownloadTask):

    def __init__(
        self,
        url: str,
        file: str
    ) -> None:
        super().__init__(url, file, is_stream=True)

    def post_process_content(self, content: bytes) -> bytes:
        return content


class SRTSubtitleDownloadTask(BaseCoroutineDownloadTask):

    def __init__(
        self,
        url: str,
        file: str
    ) -> None:
        super().__init__(url, file, is_stream=False)

    def post_process_content(self, content: bytes) -> bytes:
        return convert_to_srt(content)
