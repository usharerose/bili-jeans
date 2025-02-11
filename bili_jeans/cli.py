"""
Command-Line interface
"""
import asyncio
import click
from typing import Optional

from .app import download
from .core.constants import CodecId, QualityNumber


@click.group()
def cli():
    pass


@cli.command(name='download')
@click.option(
    '--url',
    type=str,
    required=True,
    help='URL of video'
)
@click.option(
    '--dir-path',
    type=str,
    required=True,
    help='Directory where video would be saved'
)
@click.option(
    '--qn',
    default=None,
    type=click.Choice([
        str(value.quality_id)
        for _, value in QualityNumber.__members__.items()
    ]),
    help='Quality number of video'
)
@click.option(
    '--reverse-qn',
    is_flag=True,
    default=False,
    help='Prefer higher video quality or not'
)
@click.option(
    '--codec-id',
    default=None,
    type=click.Choice([
        str(value.quality_id)
        for _, value in CodecId.__members__.items()
    ]),
    help='Codec ID of video'
)
@click.option(
    '--reverse-codec',
    is_flag=True,
    default=False,
    help='Prefer more efficient video compression standard or not'
)
@click.option(
    '--bit-rate-id',
    default=None,
    type=int,
    help='Bit rate ID of video'
)
@click.option(
    '--reverse-bit-rate',
    is_flag=True,
    default=False,
    help='Prefer higher bit rate or not'
)
@click.option(
    '--enable-danmaku',
    is_flag=True,
    default=False,
    help='Download danmaku of video'
)
@click.option(
    '--enable-cover',
    is_flag=True,
    default=False,
    help='Download cover of video'
)
@click.option(
    '--enable-subtitle',
    is_flag=True,
    default=False,
    help='Download subtitle of video'
)
@click.option(
    '--sess-data',
    default=None,
    type=str,
    help='Session data as personal certification'
)
def download_command(
    url: str,
    dir_path: str,
    qn: Optional[int] = None,
    reverse_qn: bool = False,
    codec_id: Optional[int] = None,
    reverse_codec: bool = False,
    bit_rate_id: Optional[int] = None,
    reverse_bit_rate: bool = False,
    enable_danmaku: bool = False,
    enable_cover: bool = False,
    enable_subtitle: bool = False,
    sess_data: Optional[str] = None
) -> None:
    asyncio.run(download(
        url=url,
        dir_path=dir_path,
        qn=qn,
        reverse_qn=reverse_qn,
        codec_id=codec_id,
        reverse_codec=reverse_codec,
        bit_rate_id=bit_rate_id,
        reverse_bit_rate=reverse_bit_rate,
        enable_danmaku=enable_danmaku,
        enable_cover=enable_cover,
        enable_subtitle=enable_subtitle,
        sess_data=sess_data
    ))


if __name__ == '__main__':
    cli()
