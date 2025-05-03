"""
Command-Line interface
"""
import asyncio
import os
from typing import Any, List, Optional

import click
from click import Context, Parameter

from .download import run as run_download
from ..core.constants import BitRateId, CodecId, QualityNumber
from ..core.log import config_logging, LOG_MODE_CLI


class IntListParamType(click.ParamType):

    name = 'integer_list'

    def convert(
        self,
        value: Any,
        param: Optional[Parameter],
        ctx: Optional[Context]
    ) -> Optional[List[int]]:
        try:
            if not value:
                return None
            return [int(x.strip()) for x in value.split(',')]
        except ValueError:
            self.fail(
                f'"{value}" is not a valid comma-separated integer list',
                param,
                ctx
            )


INT_LIST = IntListParamType()


@click.group()
def cli():
    config_logging(mode=LOG_MODE_CLI)
    pass


@cli.command(name='download')
@click.argument(
    'URL',
    type=str,
    required=True
)
@click.option(
    '-d',
    '--directory',
    type=str,
    default=os.getcwd(),
    help='Directory where video would be saved'
)
@click.option(
    '-p',
    '--pages',
    type=INT_LIST,
    default=None,
    help='Selected pages'
)
@click.option(
    '-q',
    '--quality-number',
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
    type=click.Choice([
        str(value.quality_id)
        for _, value in BitRateId.__members__.items()
    ]),
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
def download(
    url: str,
    directory: str,
    pages: Optional[List[int]] = None,
    quality_number: Optional[int] = None,
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
    asyncio.run(run_download(
        url=url,
        directory=directory,
        page_indexes=pages,
        qn=quality_number,
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
