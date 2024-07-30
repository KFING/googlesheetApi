import os
import logging
import pytubefix
import re
import time
from pytubefix import YouTube, Channel, Playlist
from datetime import datetime
from typing import NamedTuple, Dict, Any, Set, List, Optional
from feed_rec_info import FeedRecInfo


CWD = os.getcwd()
RESULTS_DIR = os.path.join(CWD, 'data', 'youtube')


py_logger = logging.getLogger(f"{__name__}")
py_logger.setLevel(logging.INFO)
py_handler = logging.FileHandler(f"{__name__}.log", mode='w')
py_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
py_handler.setFormatter(py_formatter)
py_logger.addHandler(py_handler)



class AudioError(Exception):
    def __init__(self, message: str, exception: Exception) -> None:
        self.exception = exception
        self.message = message


class VideoError(Exception):
    def __init__(self, message: str, exception: Exception) -> None:
        self.exception = exception
        self.message = message


class ContentError(Exception):
    def __init__(self, message: str, exception: Exception) -> None:
        self.exception = exception
        self.message = message


class CaptionError(Exception):
    def __init__(self, message: str, exception: Exception) -> None:
        self.exception = exception
        self.message = message


def get_description(yt: YouTube) -> str:
    return yt.description


def get_header(yt: YouTube) -> str:
    return yt.title


def get_post_date(yt: YouTube) -> datetime:
    return yt.publish_date


def download_audio(yt: YouTube, abr: str) -> str:
    yt.streams.filter(
        abr=abr
    ).first().download(
        output_path=os.path.join(RESULTS_DIR, yt.video_id, yt.channel_id),
        filename=f"{yt.video_id}.mp3"
    )


def get_audio(yt: YouTube, abr: str) -> None:
    try:
        os.makedirs(os.path.join(RESULTS_DIR, yt.video_id, yt.channel_id), exist_ok=True)
        abrs = sorted(
            set(stream.abr for stream in yt.streams.filter(type='audio')),
            key=lambda s: int(s.split('kbps')[0])
        )
        match abr:
            case 'low':
                download_audio(yt, abrs[0])
            case 'medium':
                download_audio(yt, abrs[len(abrs) // 2])
            case _:
                download_audio(yt, abrs[-1])
    except Exception as e:
        AudioError('wrong audio content', e)


def download_video(yt: YouTube, res: str) -> None:
    yt.streams.filter(
        res=res
    ).first().download(
        output_path=os.path.join(RESULTS_DIR, yt.channel_id, yt.video_id),
        filename=f"{yt.video_id}.mp4"
    )


def get_video(yt: YouTube, res: str) -> None:
    try:
        os.makedirs(os.path.join(RESULTS_DIR, yt.channel_id, yt.video_id), exist_ok=True)
        resolutions = sorted(
            set(stream.resolution for stream in yt.streams.filter(type='video')),
            key=lambda s: int(s.split('p')[0])
        )
        match res:
            case 'low':
                download_video(yt, resolutions[0])
            case 'medium':
                download_video(yt, resolutions[len(resolutions) // 2])
            case _:
                download_video(yt, resolutions[-1])
    except Exception as e:
        VideoError('wrong video content', e)


def get_header_image(yt: YouTube):
    channel = Channel(f'http://youtube.com/watch?v={yt.channel_id}')

def get_meta_info(yt: YouTube):
    return yt.metadata


def get_captions(yt: YouTube, lang: str) -> str:
    try:
        return yt.captions[lang].generate_srt_captions()
    except Exception as e:
        CaptionError('wrong caption content', e)


def get_timeline(yt: YouTube) -> List[pytubefix.Chapter]:
    return yt.chapters


def download_post(identificator: Dict[str, Any], dct_content_sections: Dict[str, bool]) -> FeedRecInfo:
    try:
        py_logger.info("start")
        post = YouTube(f'http://youtube.com/watch?v={identificator['id']}')
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
            feed_rec_info['id_channel'] = post.channel_id
        if dct_content_sections['header_image']:
            get_header_image(L, post)
        if dct_content_sections['video_quality_best']:
            get_video(yt=post, res='best')
        if dct_content_sections['video_quality_medium']:
            get_video(yt=post, res='medium')
        if dct_content_sections['video_quality_low']:
            get_video(yt=post, res='low')
        if dct_content_sections['audio_quality_best']:
            get_audio(yt=post, abr='best')
        if dct_content_sections['audio_quality_medium']:
            get_audio(yt=post, abr='medium')
        if dct_content_sections['audio_quality_low']:
            get_audio(yt=post, abr='low')

        py_logger.info("info success")
        return FeedRecInfo(
            social_media_name=identificator['source'],
            id_feed=feed_rec_info['id_feed'],
            id_channel=feed_rec_info['id_channel'],
            description=feed_rec_info['description'],
            header=feed_rec_info['header'],
            url=feed_rec_info['url'],
            post_date=get_post_date(post),
            video_link=feed_rec_info['id_feed'],
            meta_info=None,
            captions=None,
            timeline=None,
            audio_link=None,
        )
    except Exception as e:
        ContentError('wrong youtube content', e)


def youtube_scrapy_post(dct: Dict[str, Any], yt: YouTube) -> FeedRecInfo:
    try:
        py_logger.info("start")
        get_audio(
            yt=yt,
            abr=dct['abr']
        )
        py_logger.info("audio success")
        get_video(
            yt=yt,
            res=dct['res']
        )
        py_logger.info("video success")
        return FeedRecInfo(
            id_feed=yt.video_id,
            id_channel=yt.channel_id,
            description=get_description(yt=yt),
            title=get_title(yt=yt),
            url=dct['url'],
            post_date=get_post_date(yt=yt),
            meta_info=get_meta_info(yt=yt),
            captions=get_captions(yt=yt, lang=dct['lang']),
            timeline=get_timeline(yt=yt),
            audio_link=yt.video_id,
            video_link=yt.video_id,
        )
    except Exception as e:
        ContentError('wrong youtube content', e)


def youtube_scrapy_channel(source: Dict[str, Any], channel: str, dt_from: datetime = datetime.strptime('1900-06-13 09:00:15' , "%Y-%m-%d %H:%M:%S"), dt_to: datetime = datetime.now()) -> List[str]:
    try:
        py_logger.info("start")
        c = Channel(f'https://www.youtube.com/@Hohmemes/@{source['id']}')
        py_logger.info("getting urls")
        videos_urls = []
        for post in c.videos:
            if post.publish_date >= dt_from and post.publish_date < dt_to:
                videos_urls.append(post.video_id)
            time.sleep(10)
        return videos_urls
    except Exception as e:
        ContentError('wrong youtube content', e)


def youtube_scrapy_playlist(source: Dict[str, Any], channel: str, dt_from: datetime = datetime.strptime('1900-06-13 09:00:15' , "%Y-%m-%d %H:%M:%S"), dt_to: datetime = datetime.now()) -> List[str]:
    try:
        py_logger.info("start")
        p = Playlist(f'https://www.youtube.com/playlist?list={source['url']}')
        py_logger.info("getting urls")
        videos_urls = []
        for post in p.videos:
            if post.publish_date >= dt_from and post.publish_date < dt_to:
                videos_urls.append(post.video_id)
            time.sleep(10)
        return videos_urls
    except Exception as e:
        ContentError('wrong youtube content', e)
