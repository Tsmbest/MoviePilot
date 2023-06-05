from typing import Optional, Tuple, Union

from app.core import MediaInfo
from app.log import logger
from app.modules import _ModuleBase
from app.modules.plex.plex import Plex
from app.utils.types import MediaType


class PlexModule(_ModuleBase):

    plex: Plex = None

    def init_module(self) -> None:
        self.plex = Plex()

    def init_setting(self) -> Tuple[str, Union[str, bool]]:
        return "MEDIASERVER", "plex"

    def webhook_parser(self, message: dict) -> Optional[dict]:
        """
        解析Webhook报文体
        :param message:  请求体
        :return: 字典，解析为消息时需要包含：title、text、image
        """
        return self.plex.get_webhook_message(message)

    def media_exists(self, mediainfo: MediaInfo) -> Optional[dict]:
        """
        判断媒体文件是否存在
        :param mediainfo:  识别的媒体信息
        :return: 如不存在返回None，存在时返回信息，包括每季已存在所有集{type: movie/tv, seasons: {season: [episodes]}}
        """
        if mediainfo.type == MediaType.MOVIE:
            movies = self.plex.get_movies(title=mediainfo.title, year=mediainfo.year)
            if movies:
                logger.info(f"{mediainfo.get_title_string()} 在媒体库中不存在")
                return None
            else:
                logger.info(f"媒体库中已存在：{movies}")
                return {"type": MediaType.MOVIE}
        else:
            tvs = self.plex.get_tv_episodes(title=mediainfo.title,
                                            year=mediainfo.year)
            if not tvs:
                logger.info(f"{mediainfo.get_title_string()} 在媒体库中不存在")
                return None
            else:
                logger.info(f"{mediainfo.get_title_string()} 媒体库中已存在：{tvs}")
                return {"type": MediaType.TV, "seasons": tvs}

    def refresh_mediaserver(self, mediainfo: MediaInfo, file_path: str) -> Optional[bool]:
        """
        刷新媒体库
        :param mediainfo:  识别的媒体信息
        :param file_path:  文件路径
        :return: 成功或失败
        """
        items = [
            {
                "title": mediainfo.title,
                "year": mediainfo.year,
                "type": mediainfo.type,
                "category": mediainfo.category,
                "target_path": file_path
            }
        ]
        return self.plex.refresh_library_by_items(items)