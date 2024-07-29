import os
import logging
import time
from typing import NamedTuple, Dict, Any, Set, List, Optional, Tuple
from feed_rec_info import FeedRecInfo
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from config import API_ID, API_HASH  # получение айди и хэша нашего приложения из файла config.py
import asyncio
from telethon.errors.rpcerrorlist import FloodWaitError


CWD = os.getcwd()
RESULTS_DIR = os.path.join(CWD, 'data', 'telegram')


py_logger = logging.getLogger(f"{__name__}")
py_logger.setLevel(logging.INFO)
py_handler = logging.FileHandler(f"{__name__}.log", mode='w')
py_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
py_handler.setFormatter(py_formatter)
py_logger.addHandler(py_handler)


async def get_channel_id(client, link: str)->str:
    m = await client.get_messages(link, limit=1)
    channel_id = m[0].peer_id.channel_id
    return str(channel_id)


def clearify_text(message)->str:
    text = message.message
    text_splitted = text.split()
    text_listed = [word for word in text_splitted if word != ' ']
    return " ".join(text_listed)


async def download_media(client, message, message_id:str, channel_id:str) -> None:
    os.makedirs(os.path.join(RESULTS_DIR, channel_id, message_id), exist_ok=True)
    await client.download_media(message=message, file=os.path.join(RESULTS_DIR, channel_id, message_id, message_id))


def get_message_content(client, message, url:str, channel_id:str, message_id:str)->FeedRecInfo:
    return FeedRecInfo(
        social_media_name='telegram',
        id_feed=message_id,
        id_channel=channel_id,
        description=clearify_text(message=message),
        title=channel_id,
        url=f'{url}/{str(message.id)}',
        post_date=message.date,
        meta_info=None,
        captions=None,
        timeline=None,
        audio_link=None,
        video_link=message_id,
    )


async def parse(client, url:str):
    err = []
    feed_rec_list = []
    channel_id = await get_channel_id(client, url)
    async for message in client.iter_messages(url, reverse=True):
        try:
            feed_rec_list.append(get_message_content(client, message, url, channel_id, str(message.id)))
            time.sleep(10)
            if message.media:
                await download_media(client, message, str(message.id), channel_id)
        except Exception as passing:
            err.append(passing)
            continue
    return feed_rec_list


async def main(dct: Dict[str, Any]) -> None:
    async with TelegramClient('new', API_ID, API_HASH) as client:
        try:
            await client(JoinChannelRequest(dct['url']))
            feed_rec_list = await parse(client, dct['url'])
        except FloodWaitError as fwe:
            await asyncio.sleep(delay=fwe.seconds)
    return feed_rec_list



def main_telegram_scraper(dct: Dict[str, Any]) -> List[FeedRecInfo]:
    return asyncio.run(main(dct))
