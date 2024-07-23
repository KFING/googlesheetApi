from datetime import datetime
from typing import NamedTuple, Dict, Any, Set, List, Optional
from pytubefix import Chapter


class FeedRecInfo(NamedTuple):
    description: str
    title: str
    url: str
    postDt: datetime
    metaInfo: List[str]
    captions: str
    timeline: List[Chapter]
    Audio_link: str
    Video_link: str

    def to_dict(self) -> Dict[str, Any]:
        dct = self._asdict()
        dct['postDt'] = self.postDt.isoformat()
        dct['metaInfo'] = str(self.metaInfo)
        dct['timeline'] = str(self.captions)
        return dct
