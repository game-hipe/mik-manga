from typing import Type, Optional
from urllib.parse import urlparse

from aiohttp import ClientSession
from loguru import logger

from ..entites.schemas import ChapterSchema, MangaSchema
from ..abstract.spider import BaseSpider
from ..abstract.find import BaseFindEngine
from ..manager.request import RequestManager
from ...shared._config import SpiderConfig
from ...shared import SpiderError
from ...shared import config


class MangaService:
    """
    Сервис для управления пауками (spider'ами), отвечающими за сбор данных о манге.

    Класс загружает и инициализирует переданные пауки, обеспечивая единый интерфейс
    для поиска, получения информации о манге, главах и жанрах. Выбирает нужный паук
    на основе домена URL.

    Attributes:
        spider_config (SpiderConfig): Конфигурация для пауков. Если не передана,
            используется глобальная конфигурация.
        loaded_spider (list[BaseSpider]): Список успешно загруженных экземпляров пауков.

    Args:
        session (RequestManager | ClientSession): HTTP-сессия для выполнения запросов.
            Может быть экземпляром `RequestManager` или `aiohttp.ClientSession`.
        spiders (list[Type[BaseSpider]]): Список классов пауков, которые необходимо загрузить.
        spider_config (SpiderConfig | None): Опциональная конфигурация для пауков.
            Если не указана, используется значение из глобальной конфигурации.

    Raises:
        SpiderError: Если не удалось загрузить ни одного паука из переданного списка.

    Example:
        >>> service = MangaService(session, [ReadMangaSpider, MangaLibSpider])
        >>> manga = await service.get_manga("https://multi-manga.today/manga/title")
    """

    def __init__(
        self,
        session: RequestManager | ClientSession,
        spiders: list[Type[BaseSpider]],
        *,
        spider_config: SpiderConfig | None = None
    ) -> None:
        self.spider_config = spider_config or config.spider_config
        self._loaded_spider: list[BaseSpider] = []

        for Spider in spiders:
            try:
                spider = Spider(
                    session=session,
                    **self.spider_config.model_dump()
                )
            except Exception as e:
                logger.error(f"Ошибка при загрузке паука: {e}")
            else:
                self._loaded_spider.append(spider)

        if not self._loaded_spider:
            logger.error("Не удалось загрузить ни одного паука!")
            raise SpiderError("Не удалось загрузить ни одного паука!")

        logger.info(f"Удалось загрузить {len(self._loaded_spider)} из {len(spiders)}")

    async def get_manga(self, url: str) -> Optional[MangaSchema]:
        """
        Получает полную информацию о манге по указанному URL.

        Определяет подходящий паук по домену URL и вызывает его метод `get_manga`.
        Если соответствующий паук не найден, возвращает None.

        Args:
            url (str): URL страницы манги.

        Returns:
            MangaSchema | None: Объект с данными о манге или None, если паук не найден.

        Example:
            >>> manga = await service.get_manga("https://multi-manga.today/15145-seks-brata-i-sestry-v-gostinoj-kak-nechto-obydennoe-siblings-having-sex-in-the-living-room-like-its-normal.html")
            >>> if manga:
            >>>     print(manga.title)
        """
        for spider in self._loaded_spider:
            domen = urlparse(spider.BASE_URL).netloc
            if urlparse(url).netloc == domen:
                logger.info(f"Удалось получит мангу (site={spider.BASE_URL})")
                return await spider.get_manga(url)

        logger.warning(f"Не найден ни одни паук с данным URL: {url}")
        return None

    async def get_chapter(self, url: str) -> Optional[ChapterSchema]:
        """
        Получает данные о главе манги по указанному URL.

        Определяет подходящий паук по домену и вызывает его метод `get_manga_chapter`.
        Если паук не найден, возвращает None.

        Args:
            url (str): URL страницы главы манги.

        Returns:
            ChapterSchema | None: Объект с данными главы или None, если паук не найден.

        Example:
            >>> chapter = await service.get_chapter("https://multi-manga.today/15145-seks-brata-i-sestry-v-gostinoj-kak-nechto-obydennoe-siblings-having-sex-in-the-living-room-like-its-normal.html")
            >>> if chapter:
            >>>     print(chapter.pages)
        """
        for spider in self._loaded_spider:
            domen = urlparse(spider.BASE_URL).netloc
            if urlparse(url).netloc == domen:
                logger.info(f"Удалось получить главу (site={spider.BASE_URL})")
                return await spider.get_manga_chapter(url)

        logger.warning(f"Не найден ни одни паук с данным URL: {url}")
        return None

    async def find_manga(self, query: str, site: str) -> BaseFindEngine:
        """
        Ищет мангу по текстовому запросу на указанном сайте.

        Определяет паука по домену и вызывает его метод `find_manga`.
        Возвращает результат поиска в виде объекта `BaseFindEngine`.

        Args:
            query (str): Поисковый запрос (название манги).
            site (str): Домен сайта (например, 'multi-manga.today').

        Returns:
            BaseFindEngine: Результаты поиска. Если паук не найден, возвращает None.

        Example:
            >>> results = await service.find_manga("Брат", "multi-manga.today")
            >>> for manga in results:
            >>>     print(manga.title)
        """
        for spider in self._loaded_spider:
            domen = urlparse(spider.BASE_URL).netloc
            if site == domen:
                logger.info(f"Удалось инцилизировать поиск (site={spider.BASE_URL})")
                return await spider.find_manga(query)

        logger.warning(f"Не найден ни одни паук с данным URL: {site}")
        return None

    async def find_manga_genres(self, genres: list[str], site: str) -> BaseFindEngine:
        """
        Ищет мангу по списку жанров на указанном сайте.

        Определяет подходящий паук по домену и вызывает метод `find_manga_genres`.
        Возвращает отфильтрованные по жанрам результаты.

        Args:
            genres (list[str]): Список жанров для поиска (например, ['боевик', 'сёнен']).
            site (str): Домен сайта.

        Returns:
            BaseFindEngine: Результаты поиска. Если паук не найден, возвращает None.

        Example:
            >>> results = await service.find_manga_genres(["боевик", "фантастика"], "multi-manga.today")
            >>> for manga in results:
            >>>     print(manga.title)
        """
        for spider in self._loaded_spider:
            domen = urlparse(spider.BASE_URL).netloc
            if site == domen:
                logger.info(f"Удалось инцилизировать поиск по жанрам (site={spider.BASE_URL})")
                return await spider.find_manga_genres(genres)

        logger.warning(f"Не найден ни одни паук с данным URL: {site}")
        return None

    async def get_genres(self, site: str) -> list[str]:
        """
        Получает список доступных жанров на указанном сайте.

        Вызывает метод `get_genres` у соответствующего паука. Полезно для построения
        интерфейса с фильтрацией по жанрам.

        Args:
            site (str): Домен сайта.

        Returns:
            list[str]: Список жанров. Если паук не найден, возвращает пустой список.

        Example:
            >>> genres = await service.get_genres("multi-manga.today")
            >>> print(genres)  # ['боевик', 'драма', 'романтика', ...]
        """
        for spider in self._loaded_spider:
            domen = urlparse(spider.BASE_URL).netloc
            if site == domen:
                logger.info(f"Удалось получить список жанров (site={spider.BASE_URL})")
                return await spider.get_genres()

        logger.warning(f"Не найден ни одни паук с данным URL: {site}")
        return []

    def get_spiders(self, site: str) -> BaseSpider | None:
        """
        Получает паука по домену сайта.
        
        Args:
            site (str): Домен сайта.
            
        Returns:
            BaseSpider: Паук, соответствующий сайту. Если паук не найден, возвращает None.
            
        Example:
            >>> spider = service.get_spiders("multi-manga.today")
            >>> if spider:
            >>>        print(spider.BASE_URL)
            >>> # Output: https://multi-manga.today
        """
        for spider in self._loaded_spider:
            if site == urlparse(spider.BASE_URL).netloc:
                logger.info(f"Удалось получить паука (site={spider.BASE_URL})")
                return spider

        logger.warning(f"Не найден ни одни паук с данным URL: {site}")
        return None
    
    def get_by_id(self, id: str) -> BaseSpider | None:
        """Возращает паука по id"""
        for spider in self._loaded_spider:
            spider_id = spider.__class__.__name__.lower()
            if id == spider_id:
                logger.info(f"Удалось получить паука (id={spider_id})")
                return spider
            
        logger.warning(f"Не найден ни одни паук с данным ID: {id}")
        return None
    
    @property
    def loaded_spiders(self) -> list[BaseSpider]:
        """Возращает список загруженных пауков."""
        return self._loaded_spider