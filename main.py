import json
import lzma
import os
import logging
from scrapers.youtube_scrap import youtube_scrap_main
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


def save_to_disk(info: FeedRecInfo, article_id: str) -> None:
    os.makedirs(os.path.join(RESULTS_DIR, article_id), exist_ok=True)
    with open(os.path.join(RESULTS_DIR, article_id, f'json{article_id}.json'), "wb") as file:
        file.write(json.dumps(info.to_dict()).encode('UTF-8'))


def main() -> None:

    dct1 = {'lang': 'a.ru', 'url': 'https://www.youtube.com/watch?v=M_vDEmq3i78', 'abr': '160kpbs', 'res': '360p'}
    dct = {'lang': 'en', 'url': 'https://www.youtube.com/watch?v=aLPk8yRq9_c', 'abr': '160kpbs', 'res': '360p'}
    feed_rec_info = youtube_scrap_main(dct=dct)
    save_to_disk(info=feed_rec_info, article_id=feed_rec_info.url.split('=')[-1])
    print(feed_rec_info)


if __name__ == '__main__':
    main()


#пробелма с сериализатором в timeline и metadata, я не могу сериализовать для json эти данные и поэтому временно решил использовать превращение в строку