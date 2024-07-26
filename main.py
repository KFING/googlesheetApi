import json
import lzma
import os
import logging
from scrapers.youtube_scrapy import main_youtube_scraper
from scrapers.instagram_scrapy import main_instagram_scrapy
from scrapers.telegram_scrapy import telegram_scrapy_main
from config import API_ID, API_HASH, PHONE, INSTA_PASSWORD, INSTA_USERNAME
from feed_rec_info import FeedRecInfo
from datetime import datetime
from typing import NamedTuple, Dict, Any, Set, List, Optional


CWD = os.getcwd()
RESULTS_DIR = os.path.join(CWD, 'data')


py_logger = logging.getLogger(f"{__name__}")
py_logger.setLevel(logging.INFO)
py_handler = logging.FileHandler(f"{__name__}.log", mode='w')
py_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
py_handler.setFormatter(py_formatter)
py_logger.addHandler(py_handler)


class DownloadError(Exception):
    def __init__(self, message: str, exception: Exception) -> None:
        self.exception = exception
        self.message = message


def save_to_disk(info: FeedRecInfo) -> None:
    os.makedirs(os.path.join(RESULTS_DIR, info.id_feed, info.id_channel), exist_ok=True)
    with open(os.path.join(RESULTS_DIR, info.id_feed, info.id_channel, f'json{info.id_feed}.json'), "wb") as file:
        file.write(json.dumps(info.to_dict()).encode())


def main() -> None:
    py_logger.info("start")
    message_user = input("input res: ")
    feed_rec_list = []
    match message_user:
        case 'youtube':
            py_logger.info("youtube content")
            dct = {'lang': 'en', 'url': 'https://youtube.com/playlist?list=PLVt7fiIBvDPFdtu-_7Mm-eVgT6sLxVKDj&si=PYZ50OlyR31CfzKd', 'abr': 'low', 'res': 'low'}
            feed_rec_list = main_youtube_scraper(dct=dct)
            py_logger.info("youtube content success")
        case 'instagram':
            py_logger.info("instagram content")
            dct = {
                'lang': 'en',
                'url': 'https://www.instagram.com/p/B0QTtXKi3u_/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==',
                'abr': 'low',
                'res': 'low',
                'api_id': API_ID,
                'api_hash': API_HASH,
                'phone': PHONE,
                'insta_username': INSTA_USERNAME,
                'insta_password': INSTA_PASSWORD,
            }
            feed_rec_list = main_instagram_scrapy(dct=dct)
            py_logger.info("instagram content success")
        case 'telegram':
            dct = {'lang': 'en', 'url': 'https://t.me/masterbinarylog/2206', 'abr': '160kpbs',
                   'res': '360p', 'api_id': API_ID, 'api_hash': API_HASH, 'phone': PHONE}
            feed_rec_info = telegram_scrapy_main(dct)
        case _:
            print('hi')
    for feed_rec_info in feed_rec_list:
        save_to_disk(info=feed_rec_info)


if __name__ == '__main__':
    main()
