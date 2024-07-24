import json
import lzma
import os
import logging
from scrapers.youtube_scrap import youtube_scrap_main
from scrapers.instagram_scrap import instagram_scrap_main
from scrapers.telegram_scrap import telegram_scrap_main
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


def save_to_disk(info: FeedRecInfo, article_id: str) -> None:
    os.makedirs(os.path.join(RESULTS_DIR, article_id), exist_ok=True)
    with open(os.path.join(RESULTS_DIR, article_id, f'json{article_id}.json'), "wb") as file:
        file.write(json.dumps(info.to_dict()).encode('UTF-8'))


def main() -> None:
    py_logger.info("start")
    try:
        message_user = input("input res: ")
        match message_user:
            case 'youtube':
                py_logger.info("youtube content")
                dct = {'lang': 'en', 'url': 'https://www.youtube.com/watch?v=aLPk8yRq9_c', 'abr': '160kpbs', 'res': '360p'}
                #video1: https://www.youtube.com/watch?v=M_vDEmq3i78
                #video2: https://www.youtube.com/watch?v=aLPk8yRq9_c
                feed_rec_info = youtube_scrap_main(dct=dct)
                article_id=feed_rec_info.url.split('=')[-1]
            case 'instagram':
                py_logger.info("instagram content")
                dct = {'lang': 'en', 'url': 'https://www.youtube.com/watch?v=aLPk8yRq9_c', 'abr': '160kpbs', 'res': '360p'}
                # video post: https://www.instagram.com/reel/C9cdQhBsvay/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==
                # imageS post: https://www.instagram.com/p/C9jhuXlKEN9/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==
                # image: https://www.instagram.com/p/B0QTtXKi3u_/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==
                feed_rec_info = instagram_scrap_main(dct=dct)
                article_id = feed_rec_info.url.split('/')[-2]
            case 'telegram':
                dct = {'lang': 'en', 'url': 'https://t.me/masterbinarylog/2206', 'abr': '160kpbs',
                       'res': '360p', 'api_id': 'number', 'api_hash': 'number', 'phone': 'number'}
                feed_rec_info = telegram_scrap_main(dct)
                article_id = feed_rec_info.url.split('/')[-1]
            case _:
                print('hi')
        save_to_disk(info=feed_rec_info, article_id=article_id)
    except Exception as e:
        DownloadError('wrong content', e)


if __name__ == '__main__':
    main()


#пробелма с сериализатором в timeline и metadata, я не могу сериализовать для json эти данные и поэтому временно решил использовать превращение в строку
#есть проблема с кодировкой
#спросить про гитигнор