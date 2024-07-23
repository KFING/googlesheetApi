import os
import logging
import pytubefix
from pytubefix import YouTube
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



class AudioError(Exception):
    def __init__(self, message: str, exception: Exception) -> None:
        self.exception = exception
        self.message = message


class VideoError(Exception):
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


def get_postDt(yt: YouTube) -> datetime:
    return yt.publish_date


def get_audio(yt: YouTube, abr: str, id_video: str) -> None:
    os.makedirs(os.path.join(RESULTS_DIR, id_video), exist_ok=True)
    try:
        yt.streams.filter(only_audio=True).first().download(output_path=os.path.join(RESULTS_DIR, id_video), filename=f"{id_video}.mp3")
    except Exception as e:
        AudioError('wrong audio content', e)


def get_video(yt: YouTube, res: str, id_video: str) -> None:
    os.makedirs(os.path.join(RESULTS_DIR, id_video), exist_ok=True)
    try:
        yt.streams.filter(res=res).first().download(output_path=os.path.join(RESULTS_DIR, id_video), filename=f"{id_video}.mp4")
    except Exception as e:
        VideoError('wrong video content', e)


def get_metaInfo(yt: YouTube) -> Optional[pytubefix.metadata.YouTubeMetadata]:
    return yt.metadata


def get_captions(yt: YouTube, lang: str) -> str:
    try:
        return yt.captions[lang].generate_srt_captions()
    except Exception as e:
        CaptionError('wrong caption content', e)


def get_timeline(yt: YouTube) -> List[pytubefix.Chapter]:
    return yt.chapters


def youtube_scrap_main(dct: Dict[str, Any]) -> FeedRecInfo:
    py_logger.info("start")
    link = "https://www.youtube.com/watch?v=M_vDEmq3i78"
    yt = YouTube(dct['url'])
    get_audio(yt=yt, abr=dct['abr'], id_video=dct['url'].split("=")[-1])
    py_logger.info("audio success")
    get_video(yt=yt, res=dct['res'], id_video=dct['url'].split("=")[-1])
    py_logger.info("video success")
    return FeedRecInfo(
        description=get_description(yt=yt),
        title=get_title(yt=yt),
        url=dct['url'],
        postDt=get_postDt(yt=yt),
        metaInfo=get_metaInfo(yt=yt),
        captions=get_captions(yt=yt, lang=dct['lang']),
        timeline=get_timeline(yt=yt),
        Audio_link=dct['url'].split("=")[-1],
        Video_link=dct['url'].split("=")[-1],
    )
