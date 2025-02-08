"""
Utilities to convert Bilibili-provided JSON subtitle to general format
"""
import datetime
from io import StringIO
import json

from ..schemes import SubTitle


def convert_to_srt(content: bytes) -> bytes:
    data = json.loads(content.decode('utf-8'))
    dm = SubTitle.model_validate(data)

    converted = StringIO()
    for idx, item in enumerate(dm.body, start=1):
        converted.write(f'{idx}\n')

        from_seconds = item.from_field
        to_seconds = item.to
        converted.write(
            f'{_format_seconds(from_seconds)} --> {_format_seconds(to_seconds)}\n'
        )

        converted.write(f'{item.content}\n')

        converted.write('\n')
    return converted.getvalue().encode('utf-8')


def _format_seconds(seconds: float) -> str:
    """
    convert numeric seconds to 'hh:mm:ss,fff'
    """
    delta = datetime.timedelta(seconds=seconds)
    _hours, _remain_seconds = divmod(delta.seconds, 3600)
    _minutes, _seconds = divmod(_remain_seconds, 60)
    _milliseconds = delta.microseconds // 1000
    return f'{_hours:02}:{_minutes:02}:{_seconds:02},{_milliseconds:03}'
