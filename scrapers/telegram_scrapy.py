import asyncio
import os
import logging
import re
from datetime import datetime
from typing import NamedTuple, Dict, Any, Set, List, Optional, Tuple
from feed_rec_info import FeedRecInfo
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel


CWD = os.getcwd()
RESULTS_DIR = os.path.join(CWD, 'data', 'telegram')


py_logger = logging.getLogger(f"{__name__}")
py_logger.setLevel(logging.INFO)
py_handler = logging.FileHandler(f"{__name__}.log", mode='w')
py_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
py_handler.setFormatter(py_formatter)
py_logger.addHandler(py_handler)
class ContentError(Exception):
    def __init__(self, message: str, exception: Exception) -> None:
        self.exception = exception
        self.message = message


async def main(client: TelegramClient, phone: str, post_link: str) -> tuple[Any, Any, Any, str | Any]:
    await client.start(phone)
    match = re.match(r'https://t.me/(c/)?([^/]+)/(\d+)', post_link)
    if not match:
        py_logger.warning('Incorrect link to post')
        return
    channel_prefix, channel_identifier, message_id = match.groups()
    if channel_prefix:
        channel_entity = await client.get_entity(int(channel_identifier))
    else:
        channel_entity = await client.get_entity(channel_identifier)
    history = await client(GetHistoryRequest(
        peer=channel_entity,
        offset_id=int(message_id)+1,
        offset_date=datetime.now(),
        add_offset=0,
        limit=1,
        max_id=0,
        min_id=0,
        hash=0
    ))
    if history.messages:
        message = history.messages[0]
        if message.media:
            os.makedirs(os.path.join(RESULTS_DIR, str(message_id)), exist_ok=True)
            file_path = await client.download_media(message.media, file=os.path.join(RESULTS_DIR, str(message_id), str(message_id)))
            py_logger.info(f'The media file is saved along the path: {file_path}')
        else:
            py_logger.warning('Media files are missing from the message')
        return message.message, message.date, message.from_id, message_id
    else:
        py_logger.warning('Message not found')


def telegram_scrapy_main(dct: Dict[str, Any]):
    py_logger.info("start")
    try:
        client = TelegramClient('session_name', dct['api_id'], dct['api_hash'])
        with client:
            content, postDt, title, mes_id = asyncio.run(main(client, dct['phone'], dct['url']))
        py_logger.info("finish, all information received")
        return FeedRecInfo(
            description=content,
            title=title,
            url=dct['url'],
            postDt=postDt,
            audio_link=mes_id,
            video_link=mes_id,
            metaInfo=None,
            captions=None,
            timeline=None,
        )
    except Exception as e:
        ContentError('wrong telegram content', e)
