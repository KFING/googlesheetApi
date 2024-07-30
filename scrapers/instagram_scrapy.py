import os
import logging
import re
import asyncio
import time
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


def download_video(L: Instaloader, filename, url: str, i:int = 0) -> None:
    os.makedirs(filename, exist_ok=True)
    L.download_pic(filename=os.path.join(filename, str(i)), url=url)


def get_header_image(L: Instaloader, post: Post) -> None:
    profile_url  = post.owner_profile.profile_pic_url
    download_video(L, os.path.join(RESULTS_DIR, get_id_channel(post), get_id_post(post)), profile_url)


def get_insta_media(L: Instaloader, post: Post) -> None:
    try:
        i = 0
        if post.typename == 'GraphSidecar':
            for node in post.get_sidecar_nodes():
                if node.is_video:
                    download_video(L, filename=os.path.join(RESULTS_DIR, get_id_channel(post), get_id_post(post)),
                                   url=node.video_url, i=i)
                else:
                    download_video(L, filename=os.path.join(RESULTS_DIR, get_id_channel(post), get_id_post(post)),
                                   url=node.display_url, i=i)
                i += 1
        elif post.is_video:
            download_video(L, filename=os.path.join(RESULTS_DIR, get_id_channel(post), get_id_post(post)),
                           url=post.video_url, i=i)
        else:
            download_video(L, filename=os.path.join(RESULTS_DIR, get_id_channel(post), get_id_post(post)), url=post.url, i=i)
    except Exception as e:
        VideoError('wrong video content', e)


def get_description(post: Post) -> str:
    return post.caption


def get_header(post: Post) -> str:
    return post.owner_username


def get_post_date(post: Post) -> datetime:
    return post.date


def get_url(post: Post) -> str:
    return post.url


def get_id_post(post: Post) -> str:
    return post.shortcode


def get_id_channel(post: Post) -> str:
    return str(post.owner_id)


def download_post(identificator: Dict[str, Any], dct_content_sections: Dict[str, bool]) -> FeedRecInfo:
    py_logger.info("    start")
    L = Instaloader()
    try:
        L.login(identificator['insta_username'], identificator['insta_password'])
    except TwoFactorAuthRequiredException as e:
        L.two_factor_login(input('code for insta: '))
    try:
        post = Post.from_shortcode(L.context, identificator['id'])
        feed_rec_info = {
            'social_media_name': identificator['source'],
            'id_feed': identificator['id'],
            'id_channel': None,
            'description': None,
            'header': None,
            'url': identificator['id'],
            'post_date': None,
            'meta_info': None,
            'captions': None,
            'timeline': None,
            'audio_link': None,
            'video_link': None,
        }
        if dct_content_sections['header']:
            feed_rec_info['header'] = get_header(post)
        if dct_content_sections['description']:
            feed_rec_info['description'] = get_description(post)
        if dct_content_sections['id']:
            feed_rec_info['id_channel'] = get_id_channel(post)
        if dct_content_sections['header_image']:
            get_header_image(L, post)
        if dct_content_sections['video_quality_best']:
            get_insta_media(L, post)
        py_logger.info("info success")
        return FeedRecInfo(
            social_media_name=identificator['source'],
            id_feed=feed_rec_info['id_feed'],
            id_channel=feed_rec_info['id_channel'],
            description=feed_rec_info['description'],
            header=feed_rec_info['header'],
            url=get_url(post),
            post_date=get_post_date(post),
            video_link=feed_rec_info['id_feed'],
            meta_info=None,
            captions=None,
            timeline=None,
            audio_link=None,
        )
    except Exception as e:
        ContentError('wrong instagram content', e)


async def get_posts_list(source: Dict[str, Any], channel: str, dt_from: datetime = datetime.strptime('1900-06-13 09:00:15' , "%Y-%m-%d %H:%M:%S"), dt_to: datetime = datetime.now()) -> List[str]:
    py_logger.info("start")
    L = Instaloader()
    try:
        L.login(source['insta_username'], source['insta_password'])
    except TwoFactorAuthRequiredException as e:
        L.two_factor_login(input('code for insta: '))
    profile = Profile.from_username(L.context, username=channel)
    posts_list = []
    for post in profile.get_posts():
        if post.date_utc >= dt_from and post.date_utc < dt_to:
            posts_list.append(post.url)
    return posts_list


