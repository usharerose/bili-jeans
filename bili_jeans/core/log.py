"""
System logger configurations

User only needs to call 'config_logging' before logging
"""
import copy
import datetime
import json
from logging import Formatter, LogRecord
from logging.config import dictConfig
from collections import OrderedDict
from typing import Literal, Optional, Sequence

import tzlocal


__all__ = ['config_logging']


DEFAULT_LOG_CONFIG_DICT = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': (
                '%(asctime)s | %(process)d | %(levelname)s | +%(lineno)d %(name)s '
                '|> %(message)s'
            ),
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'json': {
            '()': 'bili_jeans.core.log.JsonFormatter'
        },
        'cli': {
            'format': '%(asctime)s |> %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
            'stream': 'ext://sys.stdout'
        },
        'plain': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'stream': 'ext://sys.stdout'
        },
        'cli': {
            'class': 'logging.StreamHandler',
            'formatter': 'cli',
            'stream': 'ext://sys.stdout'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO'
        }
    }
}


LOG_MODE_PROD: Literal['prod'] = 'prod'
LOG_MODE_DEBUG: Literal['debug'] = 'debug'
LOG_MODE_CLI: Literal['cli'] = 'cli'


class JsonFormatter(Formatter):

    fmt_fields = (
        'asctime',
        'process',
        'levelname',
        'lineno',
        'name',
        'message'
    )

    # pylint: disable=super-init-not-called
    def __init__(
        self,
        fmt: Optional[Sequence] = None,
        datefmt: Optional[str] = None
    ):

        if fmt and not isinstance(fmt, (tuple, list)):
            raise TypeError(
                f'fmt param must be tuple or list type, current type: {type(fmt)}'
            )
        self._fmt: Sequence = fmt or self.fmt_fields  # type: ignore[assignment]

        self.datefmt = datefmt

    def _get_exception_text(self, record) -> str:
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        result = f'{record.exc_text}' if record.exc_text else ''
        return result

    def usesTime(self) -> bool:
        """
        Check if the format uses the creation time of the record.
        """
        return 'asctime' in self._fmt

    def format(self, record: LogRecord) -> str:
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        result = OrderedDict()
        for field in self._fmt:
            result[field] = record.__dict__.get(field, '')

        if record.exc_info:
            result['exc'] = self._get_exception_text(record)

        return json.dumps(result)

    def formatTime(self, record: LogRecord, datefmt: Optional[str] = None) -> str:
        ct = datetime.datetime.fromtimestamp(
            record.created,
            tzlocal.get_localzone()
        )
        if datefmt:
            result = ct.strftime(datefmt)
        else:
            time_zone = ct.strftime('%z')
            time_zone = time_zone[:-2] + ':' + time_zone[-2:]
            time_str = ct.strftime('%Y-%m-%dT%H:%M:%S')
            result = "%s.%03d%s" % (time_str, record.msecs, time_zone)
        return result


def config_logging(mode: Literal['prod', 'debug', 'cli'] = LOG_MODE_PROD):
    """
    Config logging of the system

    Args:
        mode: provide 'prod', 'debug' & 'cli' with various format
    """
    dict_config = copy.deepcopy(DEFAULT_LOG_CONFIG_DICT)
    if mode == 'debug':
        dict_config['loggers']['']['handlers'] = ['plain']  # type: ignore[index]
    elif mode == 'cli':
        dict_config['loggers']['']['handlers'] = ['cli']  # type: ignore[index]
    dictConfig(dict_config)
