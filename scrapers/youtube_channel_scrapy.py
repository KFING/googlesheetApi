import re
import os
import logging
import pytubefix
import time
from pytubefix import YouTube, Channel, Playlist
from datetime import datetime
from typing import NamedTuple, Dict, Any, Set, List, Optional
from feed_rec_info import FeedRecInfo
from feed_rec_info import FeedRecInfo
#link https://youtube.com/@hohmemes?si=zXlgflyh1yADNxlt
url = 'https://www.youtube.com/@Hohmemes/playlists'
c = Channel(url)
feed_rec_list: List[FeedRecInfo] = []
for url in c.videos:
    print(f"parsing url:{type(url)}")