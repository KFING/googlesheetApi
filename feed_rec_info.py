from datetime import datetime
from typing import NamedTuple, Dict, Any, Set, List, Optional


class FeedRecInfo(NamedTuple):
    id_feed: str
    id_channel: str
    description: str
    title: str
    url: str
    post_date: datetime
    meta_info: List[str]
    captions: str
    timeline: List[Any]
    audio_link: str
    video_link: str

    def to_dict(self) -> Dict[str, Any]:
        dct = self._asdict()
        dct['post_date'] = self.post_date.isoformat()
        dct['meta_info'] = str(self.meta_info)
        dct['timeline'] = str(self.captions)
        return dct
