import os
import logging
import re
import asyncio
from instaloader import Instaloader, Post, Profile
from datetime import datetime
from typing import NamedTuple, Dict, Any, Set, List, Optional
from feed_rec_info import FeedRecInfo
from instaloader.exceptions import TwoFactorAuthRequiredException

CWD = os.getcwd()
RESULTS_DIR = os.path.join(CWD, 'data', 'instagram')

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


def download_video(L: Instaloader, filename, url: str, date: datetime) -> None:
    os.makedirs(filename, exist_ok=True)
    L.download_pic(filename=filename, url=url, mtime=date)


def get_insta_media(L: Instaloader, post: Post) -> None:
    try:
        i = 0
        if post.typename == 'GraphSidecar':
            for node in post.get_sidecar_nodes():
                if node.is_video:
                    download_video(L, filename=os.path.join(RESULTS_DIR, get_id_channel(post), get_id_post(post), str(i)),
                                   url=node.video_url, date=post.date_utc)
                else:
                    download_video(L, filename=os.path.join(RESULTS_DIR, get_id_channel(post), get_id_post(post), str(i)),
                                   url=node.display_url, date=post.date_utc)
                i += 1
        elif post.is_video:
            download_video(L, filename=os.path.join(RESULTS_DIR, get_id_channel(post), get_id_post(post), str(i)),
                           url=post.video_url, date=post.date_utc)
        else:
            download_video(L, filename=os.path.join(RESULTS_DIR, get_id_channel(post), get_id_post(post), str(i)), url=post.url,
                           date=post.date_utc)
    except Exception as e:
        VideoError('wrong video content', e)


def get_description(post: Post) -> str:
    return post.caption


def get_title(post: Post) -> str:
    return post.owner_username


def get_date(post: Post) -> datetime:
    return post.date


def get_url(post: Post) -> str:
    return post.url


def get_id_post(post: Post) -> str:
    return post.shortcode


def get_id_channel(post: Post) -> str:
    return str(post.owner_id)


def instagram_scrapy_post(L: Instaloader, post: Post) -> FeedRecInfo:
    try:
        py_logger.info("    start")
        py_logger.info("get video")
        get_insta_media(L=L, post=post)
        py_logger.info("video success")
        return FeedRecInfo(
            description=get_description(post),
            id_feed=get_id_post(post),
            id_channel=get_id_channel(post),
            title=get_title(post),
            url=get_url(post),
            post_date=get_date(post),
            video_link=get_id_post(post),
            meta_info=None,
            captions=None,
            timeline=None,
            audio_link=None,
        )
    except Exception as e:
        ContentError('wrong instagram content', e)


def instagram_scrapy_profile(L: Instaloader, dct: Dict[str, Any]) -> List[FeedRecInfo]:
    py_logger.info("start")
    try:
        py_logger.info("start")

        feed_rec_list: List[FeedRecInfo] = []
        try:
            L.login(dct['insta_username'], dct['insta_password'])
        except TwoFactorAuthRequiredException as e:
            L.two_factor_login(input('code for insta: '))
        for post in Profile.from_username(L.context, dct['url']).get_posts():
            py_logger.info(f"get post{post.shortcode}")
            feed_rec_list.append(instagram_scrapy_post(L, post))
        py_logger.info("profile success")
        return feed_rec_list
    except Exception as e:
        ContentError('wrong instagram content', e)


def main_instagram_scrapy(dct: Dict[str, Any]) -> List[FeedRecInfo]:
    post_pattern = re.compile(r'^https?://(www\.)?instagram\.com/p/[\w-]+/?(\?[\w=&]+)?$')
    if post_pattern.match(dct['url']):
        return instagram_scrapy_profile(Instaloader(), dct)
    elif re.match(r'^[\w-]+$', dct['url']):
        return [
            instagram_scrapy_post(Instaloader(), Post.from_shortcode(Instaloader().context, dct['url'].split("/")[-2]))]
    else:
        return 'unknown'  #я не знаю что тут передавать
