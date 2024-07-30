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


py_logger.info("start")
L = Instaloader()
profile = Profile.from_username(L.context, username='egor_meschenko')
for post in profile.get_posts():
    print(datetime.now())
    print(f'date: {post.date_utc}')
    if post.date_utc >= datetime.strptime('2021-06-13 09:00:15' , "%Y-%m-%d %H:%M:%S") and post.date_utc < datetime.now():
        print(post.date_utc)



#async def download_post(identificator, content_sections) → ObjectsBySection


#async def get_posts_list(source, channel, dt_from, dt_to | None):


#async def download_post(identificator, content_sections) →

#ObjectsBySection

#identificator
#identificator={'source': 'instagram', 'id': 'https://www.instagram.com/b3r3zko?utm_source=ig_web_button_share_sheet&igsh=ZDNlZDc0MzIxNw=='}
#- Source
#- ID
#of
#post

# content_section
# content_section={'header':'true', 'description':'true', 'id':'true', 'header_image':'true', 'video_quality_best':'true', 'video_quality_medium':'true', 'video_quality_low':'true', 'audio_quality_best':'true', 'audio_quality_medium':'true', 'audio_quality_low':'true'}

#- header
#- description
#- id
#- header_image
#- video_quality_best
#- video_quality_…
#- audio_quality_best

#List
#of
#Posts

#async def get_posts_list(source, chan
# nel, dt_from, dt_to |None)