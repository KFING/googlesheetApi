import os
import logging
import re
import asyncio
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


class ContentError(Exception):
    def __init__(self, message: str, exception: Exception) -> None:
        self.exception = exception
        self.message = message


class VideoError(Exception):
    def __init__(self, message: str, exception: Exception) -> None:
        self.exception = exception
        self.message = message


def is_instagram_post_url(url):
    instagram_post_pattern = re.compile(r'^https://www\.instagram\.com/p/[^/]+/$')
    if instagram_post_pattern.match(url):
        return 'Instagram Post'
    else:
        return 'Unknown'

def get_video(L: Instaloader, post: Post, post_id: str):
    try:
        os.makedirs(os.path.join(RESULTS_DIR, post_id), exist_ok=True)
        i = 0
        if post.typename == 'GraphSidecar':
            for node in post.get_sidecar_nodes():
                if node.is_video:
                    L.download_pic(filename=os.path.join(RESULTS_DIR, post_id, str(i)), url=node.video_url,
                                   mtime=post.date_utc)
                else:
                    L.download_pic(filename=os.path.join(RESULTS_DIR, post_id, str(i)), url=node.display_url,
                                   mtime=post.date_utc)
                i += 1
        elif post.is_video:
            L.download_pic(filename=os.path.join(RESULTS_DIR, post_id, str(i)), url=post.video_url, mtime=post.date_utc)
        else:
            L.download_pic(filename=os.path.join(RESULTS_DIR, post_id, str(i)), url=post.url, mtime=post.date_utc)
    except Exception as e:
        VideoError('wrong video content', e)


def get_description(post: Post):
    return post.caption


def get_title(post: Post):
    return post.owner_username


def get_date(post: Post):
    return post.date


def instagram_scrapy_post(dct: Dict[str, Any]):
    try:
        py_logger.info("start")
        L = Instaloader()
        post_id = dct['url'].split("/")[-2]
        post = Post.from_shortcode(L.context, post_id)
        py_logger.info("get video")
        get_video(L=L, post=post, post_id=post_id)
        py_logger.info("video success")
        return FeedRecInfo(
            description=get_description(post),
            title=get_title(post),
            url=dct['url'],
            postDt=get_date(post),
            metaInfo=None,
            captions=None,
            timeline=None,
            audio_link=None,
            video_link=post_id,
        )
    except Exception as e:
        ContentError('wrong instagram content', e)


