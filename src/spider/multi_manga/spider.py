from loguru import logger

from ...core.abstract import BaseSpider
from ...core.entites.schemas import MangaSchema


class MultiMangaSpider(BaseSpider):
    BASE_URL = 'https://multi-manga.today'
    
    async def get_manga(self, url: str) -> MangaSchema:
        response = await self.engine.get(url, 'read')
        if response is None:
            logger.warning(
                "Не удалось получить страницу"
            )
            return
        
        response
        
    async def find_manga(self, query):
        return await super().find_manga(query)
    
    async def find_manga_genres(self, genres):
        return await super().find_manga_genres(genres)
    
    async def get_manga_chapter(self, url):
        return await super().get_manga_chapter(url)
    
    async def get_genres(self):
        return await super().get_genres()