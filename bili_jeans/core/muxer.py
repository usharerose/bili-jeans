"""
Process mulitple streams into one file
"""
import asyncio
import datetime
import logging
from pathlib import Path
from typing import List, Optional


logger = logging.getLogger(__name__)


async def mux_streams(
    output_file: str,
    url: str,
    title: str,
    description: str,
    author_name: str,
    publish_date: int,
    video_file: Optional[str] = None,
    audio_file: Optional[str] = None,
    cover_file: Optional[str] = None,
    overwrite: bool = False,
    preserve_original: bool = False
) -> None:
    if any([item is None for item in (video_file, audio_file)]):
        logger.warning(
            'Skipping muxing process since video or audio is not provided'
        )
        return

    video_p, audio_p = map(Path, (video_file, audio_file))  # type: ignore
    for p in (video_p, audio_p):
        if not p.exists():
            raise FileNotFoundError(f'File not found: {str(p)}')

    file_p = Path(output_file)
    for src_p in ([
        Path(file) for file in (
            video_file,
            audio_file,
            cover_file
        ) if file is not None
    ]):
        if file_p.resolve() == src_p.resolve():
            raise ValueError(
                f'Output file cannot be the same as the source file :{str(file_p)}'
            )

    file_p.parent.mkdir(parents=True, exist_ok=True)

    arguments = _build_ffmpeg_arguments(
        str(file_p),
        url,
        title,
        description,
        author_name,
        publish_date,
        str(video_p),
        str(audio_p),
        None if cover_file is None or not Path(cover_file).exists() else cover_file,
        overwrite,
    )
    await _exec_ffmpeg(arguments)

    if preserve_original:
        return

    for p in (video_p, audio_p):
        p.unlink()


def _build_ffmpeg_arguments(
    output_file: str,
    url: str,
    title: str,
    description: str,
    author_name: str,
    publish_date: int,
    video_file: str,
    audio_file: str,
    cover_file: Optional[str] = None,
    overwrite: bool = False
) -> List[str]:
    arguments: List[str] = []

    inputs_args: List[str] = []
    inputs_map_args: List[str] = []

    inputs_args.extend(['-i', video_file])
    inputs_map_args.extend(['-map', '0:v'])
    inputs_args.extend(['-i', audio_file])
    inputs_map_args.extend(['-map', '1:a'])

    attached_pic = False
    if cover_file is not None:
        inputs_args.extend(['-i', cover_file])
        inputs_map_args.extend(['-map', '2'])
        attached_pic = True

    arguments.extend(inputs_args)
    arguments.extend(inputs_map_args)
    if attached_pic:
        arguments.extend(['-disposition:v:1', 'attached_pic'])

    if overwrite:
        arguments.append('-y')
    else:
        arguments.append('-n')

    arguments.extend(['-c:v', 'copy'])  # copy video stream
    arguments.extend(['-c:a', 'copy'])  # copy audio stream

    arguments.extend(['-metadata', f'comment="{url}"'])
    arguments.extend(['-metadata', f'title="{title}"'])
    arguments.extend(['-metadata', f'description="{description}"'])
    arguments.extend(['-metadata', f'artist="{author_name}"'])
    arguments.extend(['-metadata', f'creation_time="{author_name}"'])
    arguments.extend([
        '-metadata',
        f'creation_time="{datetime.datetime.fromtimestamp(publish_date).strftime("%Y-%m-%dT%H:%M:%S.%fZ")}"'
    ])

    arguments.extend(['-progress', 'pipe:1'])  # display progress

    arguments.append(output_file)
    return arguments


async def _exec_ffmpeg(
    arguments: List[str]
) -> None:
    process = await asyncio.create_subprocess_exec(
        'ffmpeg',
        *arguments,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    _, stderr = await process.communicate()
    if process.returncode != 0:
        raise RuntimeError(
            f"ffmpeg command failed:\n{stderr.decode()}"
        )
