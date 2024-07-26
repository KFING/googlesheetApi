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


def get_title(yt: YouTube) -> str:
    return yt.title



def get_post_date(yt: YouTube) -> datetime:
    return yt.publish_date


def get_audio(yt: YouTube, abr: str) -> None:
    try:
        os.makedirs(os.path.join(RESULTS_DIR, yt.video_id, yt.channel_id), exist_ok=True)
        abrs = sorted(
            set(stream.abr for stream in yt.streams.filter(type='audio')),
            key=lambda s: int(s.split('kbps')[0])
        )
        match abr:
            case 'low':
                yt.streams.filter(
                    abr=abrs[0]
                ).first().download(
                    output_path=os.path.join(RESULTS_DIR, yt.video_id, yt.channel_id),
                    filename=f"{yt.video_id}.mp3"
                )
            case 'medium':
                yt.streams.filter(
                    abr=abrs[len(abrs) // 2]
                ).first().download(
                    output_path=os.path.join(RESULTS_DIR, yt.video_id, yt.channel_id),
                    filename=f"{yt.video_id}.mp3"
                )
            case _:
                yt.streams.filter(
                    abr=abrs[-1]
                ).first().download(
                    output_path=os.path.join(RESULTS_DIR, yt.video_id, yt.channel_id),
                    filename=f"{yt.video_id}.mp3"
                )
    except Exception as e:
        AudioError('wrong audio content', e)


def get_video(yt: YouTube, res: str) -> None:
    try:
        os.makedirs(os.path.join(RESULTS_DIR, yt.video_id, yt.channel_id), exist_ok=True)
        resolutions = sorted(
            set(stream.resolution for stream in yt.streams.filter(type='video')),
            key=lambda s: int(s.split('p')[0])
        )
        match res:
            case 'low':
                yt.streams.filter(
                    res=resolutions[0]
                ).first().download(
                    output_path=os.path.join(RESULTS_DIR, yt.video_id, yt.channel_id),
                    filename=f"{yt.video_id}.mp4"
                )
            case 'medium':
                yt.streams.filter(
                    res=resolutions[len(resolutions) // 2]
                ).first().download(
                    output_path=os.path.join(RESULTS_DIR, yt.video_id, yt.channel_id),
                    filename=f"{yt.video_id}.mp4"
                )
            case _ :
                yt.streams.filter(
                    res=resolutions[-1]
                ).first().download(
                    output_path=os.path.join(RESULTS_DIR, yt.video_id, yt.channel_id),
                    filename=f"{yt.video_id}.mp4"
                )
    except Exception as e:
        VideoError('wrong video content', e)


def get_meta_info(yt: YouTube) -> Optional[pytubefix.metadata.YouTubeMetadata]:
    return yt.metadata


def get_captions(yt: YouTube, lang: str) -> str:
    try:
        return yt.captions[lang].generate_srt_captions()
    except Exception as e:
        CaptionError('wrong caption content', e)


def get_timeline(yt: YouTube) -> List[pytubefix.Chapter]:
    return yt.chapters


def youtube_scrapy_video(dct: Dict[str, Any], yt: YouTube) -> FeedRecInfo:
    try:
        py_logger.info("start")
        get_audio(yt=yt, abr=dct['abr'])
        py_logger.info("audio success")
        get_video(yt=yt, res=dct['res'])
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


def youtube_scrapy_channel(dct: Dict[str, Any]) -> List[FeedRecInfo]:
    try:
        py_logger.info("start")
        c = Channel(dct['url'])
        py_logger.info("getting links")
        feed_rec_list: List[FeedRecInfo] = []
        for video in c.videos:
            py_logger.info(f"parsing video:{video}")
            feed_rec_info = youtube_scrapy_video(dct=dct, yt=video)
            feed_rec_list.append(feed_rec_info)
            time.sleep(10)
        return feed_rec_list
    except Exception as e:
        ContentError('wrong youtube content', e)


def youtube_scrapy_playlist(dct: Dict[str, Any]) -> List[FeedRecInfo]:
    try:
        py_logger.info("start")
        p = Playlist(dct['url'])
        py_logger.info("getting links")
        feed_rec_list: List[FeedRecInfo] = []
        for video in p.videos:
            py_logger.info(f"parsing video:{video}")
            feed_rec_info = youtube_scrapy_video(dct=dct, yt=video)
            feed_rec_list.append(feed_rec_info)
            time.sleep(10)
        return feed_rec_list
    except Exception as e:
        ContentError('wrong youtube content', e)


def main_youtube_scraper(dct: Dict[str, Any]) -> List[FeedRecInfo]:
    if re.compile(r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/(@[^&=%\?]{1,})').match(dct['url']):
        return youtube_scrapy_channel(dct=dct)
    if re.compile(r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/playlist\?list=[^&=%\?]{1,}').match(dct['url']):
        return youtube_scrapy_playlist(dct=dct)
    if re.compile(r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/post/[^&=%\?]{1,}').match(dct['url']):
        yt = YouTube(url=dct['url'])
        return [youtube_scrapy_post(dct=dct, yt=yt)]
    if re.compile(r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/watch\?v=[^&=%\?]{1,}').match(dct['url']):
        yt = YouTube(url=dct['url'])
        return [youtube_scrapy_video(dct=dct, yt=yt)]