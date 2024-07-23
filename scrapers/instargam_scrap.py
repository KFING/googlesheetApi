import os
import logging
from instaloader import Instaloader, Post
from datetime import datetime
from typing import NamedTuple, Dict, Any, Set, List, Optional
from feed_rec_info import FeedRecInfo


CWD = os.getcwd()
RESULTS_DIR = os.path.join(CWD, 'data')


py_logger = logging.getLogger(f"{__name__}")
py_logger.setLevel(logging.INFO)
py_handler = logging.FileHandler(f"{__name__}.log", mode='w')
py_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
py_handler.setFormatter(py_formatter)
py_logger.addHandler(py_handler)


def get_video(L: Instaloader, post: Post):
    L.download_post(post, target=post.owner_username)

def youtube_scrap_main():
    L = Instaloader()

    # Вставьте сюда ссылку на пост
    post_url = 'https://www.instagram.com/p/C751UsStyXd/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA=='

    # Извлечение идентификатора поста из URL
    shortcode = post_url.split("/")[-2]

    # Загрузка поста по его идентификатору
    post = Post.from_shortcode(L.context, shortcode)
    get_video(L, post)
    # Вывод информации о посте
    print(f"Автор: {post.owner_username}")
    print(f"Описание: {post.caption}")
    print(f"Количество лайков: {post.likes}")
    print(f"Количество комментариев: {post.comments}")
    print(f"Дата публикации: {post.date}")
    print(f"URL изображения: {post.url}")
    return FeedRecInfo(
        description=post.caption,
        title=post.owner_username,
        url=post.url,
        postDt=post.date,
        metaInfo=None,
        captions=None,
        timeline=None,
        audio_link=None,
        video_link=post.url,
    )


if __name__ == '__main__':
    youtube_scrap_main()