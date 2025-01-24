"""
Download resources to local
"""
import aiofile
import aiohttp

from .constants import CHUNK_SIZE, HEADERS


async def download_resource(
    url: str,
    file: str
) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url,
            headers=HEADERS
        ) as resp:
            async with aiofile.async_open(file, 'wb') as afp:
                async for chunk_data in resp.content.iter_chunked(CHUNK_SIZE):
                    await afp.write(chunk_data)  # type: ignore[attr-defined]
