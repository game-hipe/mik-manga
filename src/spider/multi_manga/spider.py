from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ...core.abstract import BaseSpider
from ...shared import FetchError
from .parser import MultiMangaParserMother
from .find import MultiMangaFindEngine


class MultiMangaSpider(BaseSpider):
    BASE_URL = "https://multi-manga.today"

    def __init__(
        self,
        session,
        parser: MultiMangaParserMother | None = None,
        find_engine: MultiMangaFindEngine | None = None,
        max_concurrents=None,
        max_retries=None,
        features=None,
    ):
        super().__init__(
            session,
            parser or MultiMangaParserMother,
            find_engine or MultiMangaFindEngine,
            max_concurrents,
            max_retries,
            features,
        )

    async def get_genres(self):
        if response := await self.engine.get(
            urljoin(self.BASE_URL, "/filter.html"), "read"
        ):
            soup = BeautifulSoup(response, self.parser.features)
            return [
                x.get_text(strip=True)
                for x in soup.select('select[name="n.m.tags"] option')
            ]

        raise FetchError(
            f"Не удалось получить список жанров с {urljoin(self.BASE_URL, '/filter.html')}"
        )
