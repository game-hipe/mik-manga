from typing import Type

import aiohttp

from loguru import logger

from .request import RequestManager
from ..abstract import BaseSpider
from ...shared._config import SpiderConfig


class SpiderManager:
    BASE_CONFIG = SpiderConfig(max_concurrents=5, max_retries=3, features="html.parser")

    def __init__(
        self,
        session: aiohttp.ClientSession | RequestManager,
        spiders: list[Type[BaseSpider]],
        config: SpiderConfig | None = None,
    ):
        self.session = session
        self.spiders = spiders
        self.config = config or self.BASE_CONFIG

        self.loaded_spiders = []
        self._setup_spiders()

    def _setup_spiders(self):
        for Spider in self.spiders:
            spider = Spider(session=self.session, **self.config)
            self.loaded_spiders.append(spider)
            logger.info(f"Паук: '{spider.BASE_URL}' загружен")

    async def get_spider(self): ...
