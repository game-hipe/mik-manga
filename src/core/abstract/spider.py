"""
Модуль для абстрактного класса паука
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Type

from aiohttp import ClientSession
from loguru import logger

from ..manager.request import RequestManager
from ..entites.schemas import (
    MangaSchema,
    ChapterSchema,
    MangaDetailSchema,
    BaseMangaSchema,
)
from .find import BaseFindEngine
from .parser import BaseParserMother


class BaseSpider(ABC):
    """
    Абстрактный базовый класс для реализации парсеров (пауков) различных ресурсов с мангой.

    Определяет интерфейс и общую логику для взаимодействия с веб-сайтами,
    включая поиск, получение информации о манге и главах.
    """

    BASE_FEATURES: str = "html.parser"
    """Базовый движок парсинга разметки по умолчанию."""

    BASE_URL: str = "https://example.manga"
    """Базовый URL целевого ресурса. Должен быть переопределен в подклассе."""

    def __init__(
        self,
        session: ClientSession | RequestManager,
        parser: Type[BaseParserMother],
        find_engine: Type[BaseFindEngine],
        max_concurrents: int | None = None,
        max_retries: int | None = None,
        features: str | None = None,
    ):
        """
        Инициализирует экземпляр парсера.

        Args:
            session: Сессия aiohttp или готовый экземпляр RequestManager.
            parser: Объект парсера для извлечения данных.
            features: Тип парсера для BeautifulSoup (например, 'lxml' или 'html.parser').
            max_concurrents: Максимальное количество одновременных запросов.
            max_retries: Максимальное количество попыток выполнения запроса.
        """
        self._session = None
        self.engine = None
        self.features = features or self.BASE_FEATURES

        self.parser = parser(self.BASE_URL, self.features)
        self.find_engine = find_engine
        self._test_args()

        if isinstance(session, RequestManager):
            self._session = session.session
            self.engine = session
        else:
            self._session = session
            self.engine = RequestManager(
                session, max_concurrents=max_concurrents, max_retries=max_retries
            )

    async def get_manga(self, url: str | BaseMangaSchema) -> MangaSchema | None:
        """
        Получает основную информацию о манге по указанному URL.

        Должен возвращать объект MangaSchema с базовыми данными и списком ссылок на главы. Иначе None.
        """
        if isinstance(url, BaseMangaSchema):
            url = str(url.url)
        else:
            url = str(url)

        if response := await self.engine.get(url, "read"):
            return self.parser.parse_manga(response)
        logger.warning(f"Не удалось получить мангу (url={url})")

    async def find_manga(self, query: str) -> BaseFindEngine:
        """
        Выполняет поиск манги по текстовому запросу.

        Возвращает список кратких информационных моделей манги.
        """
        return await self.find_engine.find(
            query=query, engine=self.engine, base_url=self.BASE_URL, parser=self.parser
        )

    async def find_manga_genres(self, genres: list[str]) -> BaseFindEngine:
        """
        Выполняет поиск манги по списку жанров.

        Возвращает список кратких информационных моделей манги, подходящих под критерии.
        """
        return await self.find_engine.find_genres(
            query=genres, engine=self.engine, base_url=self.BASE_URL, parser=self.parser
        )

    async def get_manga_chapter(self, url: str) -> ChapterSchema:
        """
        Парсит конкретную главу манги по ссылке.

        Возвращает объект ChapterSchema, содержащий изображения или текст главы.
        """
        if response := await self.engine.get(url, "read"):
            return self.parser.parse_chapter(response, url)
        logger.warning(f"Не удалось получить главу (url={url})")

    async def get_manga_full(self, url: str | BaseMangaSchema) -> MangaDetailSchema:
        """
        Собирает полную информацию о манге, включая данные всех глав.

        Метод сначала получает общую информацию, а затем параллельно
        загружает содержимое всех глав, указанных в объекте манги.

        Args:
            url: Прямая ссылка на страницу манги.

        Returns:
            Объект MangaDetailSchema с полным набором данных.
        """
        if isinstance(url, BaseMangaSchema):
            url = str(url.url)
        else:
            url = str(url)

        manga = await self.get_manga(url)
        tasks = [
            asyncio.create_task(self.get_manga_chapter(chapter_url))
            for chapter_url in manga.chapters
        ]

        chapters = await asyncio.gather(*tasks)
        mixed_chapters = {x.url: x for x in chapters}

        return MangaDetailSchema(
            title=manga.title,
            poster=manga.poster,
            url=manga.url,
            genres=manga.genres,
            author=manga.author,
            language=manga.language,
            chapters=[mixed_chapters[x] for x in manga.chapters],
        )

    @abstractmethod
    async def get_genres(self) -> list[str]:
        """
        Получает список всех доступных жанров на ресурсе.
        """

    def _test_args(self):
        """
        Проверяет корректность конфигурации парсера.

        Используется для предотвращения запуска базового класса без
        установленного адреса целевого ресурса.

        Исключения:
            NotImplementedError: Если BASE_URL не был переопределен в дочернем классе.
        """
        if self.BASE_URL == "https://example.manga":
            raise NotImplementedError(
                "BASE_URL не установлен, установите его в наследуемом классе"
            )

        if not isinstance(self.parser, BaseParserMother):
            raise TypeError(
                f"parser должен быть экземпляром BaseParserMother (type={self.parser})"
            )

        if not issubclass(self.find_engine, BaseFindEngine):
            raise TypeError("find_engine должен быть наследуемым BaseFindEngine")
