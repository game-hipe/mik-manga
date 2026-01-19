"""
Модуль поискового движка для парсинга манги.

Содержит абстрактный базовый класс BaseFindEngine, который определяет общую
структуру для реализации поисковых движков манги с различных источников.

Основные возможности:
    - Поиск манги по текстовому запросу
    - Поиск манги по жанрам
    - Навигация по страницам результатов
    - Парсинг HTML-разметки результатов

Атрибуты модуля:
    BaseFindEngine: Абстрактный базовый класс для всех поисковых движков.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import AsyncGenerator

from bs4 import _IncomingMarkup
from loguru import logger
from cachetools import TTLCache

from ..manager.request import RequestManager
from ..entites.schemas import BaseMangaSchema
from .parser import BaseParserMother
from ...shared import FindMethod

__all__ = [
    'BaseFindEngine'
]


class BaseFindEngine(ABC):
    """
    Абстрактный базовый класс для поисковых движков парсинга манги.

    Предоставляет общую структуру для реализации движков поиска манги
    по различным источникам. Включает управление страницами, базовый
    URL, настройки парсинга и взаимодействие с менеджером запросов.

    Атрибуты:
        BASE_FEATURES (str): Базовый движок парсинга разметки по умолчанию.
                            Используется, если не указан иной формат.
                            По умолчанию: "html.parser"

    Пример использования:
        class MyFindEngine(BaseFindEngine):
            @classmethod
            async def find(cls, query: str):
                # Реализация поиска
                pass

            # ... реализация других абстрактных методов
    """
    
    MAX_SIZE: int = 32
    """Максимальный размер кэша"""
    
    TTL: int = 300
    """Максимальное время жизни"""
    
    def __init__(
        self,
        query: str | list[str],
        engine: RequestManager,
        base_url: str,
        parser: BaseParserMother,
        find_method: FindMethod,
        max_size: int | None = None,
        ttl: int | None = None
    ):
        """
        Инициализирует поисковый движок.

        Создает экземпляр поискового движка с указанными параметрами.

        Args:
            engine (RequestManager): Менеджер для выполнения HTTP-запросов.
            base_url (str): Базовый URL-адрес сайта для парсинга.
            features (str | None): Формат парсера разметки (например, 'html.parser').
                                  Если None, используется значение по умолчанию.

        Атрибуты экземпляра:
            page_now (int): Текущая активная страница результатов. Начинается с 1.
            max_page (int): Максимальное количество доступных страниц.
                           Значение -1 означает, что лимит не установлен.
        """
        self.parser = parser
        self.engine = engine
        self.base_url = base_url
        
        self.page_now = 1
        self.max_page = -1
        
        if not isinstance(parser, BaseParserMother):
            raise TypeError(
                f'{self.__class__.__name__} не является подклассом BaseParserMother'
            )
        
        self.lock = asyncio.Lock()
        self.query = query
        self.find_method = find_method
        self.cashe = TTLCache(
            maxsize = max_size or self.MAX_SIZE,
            ttl = ttl or self.TTL
        )
    
    @classmethod
    @abstractmethod
    async def find(cls, query: str, engine: RequestManager, base_url: str, parser: BaseParserMother) -> BaseFindEngine:
        """
        Асинхронно выполняет поиск манги по текстовому запросу.

        Абстрактный метод, который должен быть реализован в подклассах.

        Args:
            query (str): Поисковый запрос (название манги или ключевые слова).
            engine (RequestManager): Менеджер для выполнения HTTP-запросов.
            base_url (str): Базовый URL-адрес сайта для парсинга.
            parser (BaseParserMother): Парсер для обработки HTML-разметки.


        Returns:
            list[BaseMangaSchema]: Список найденных манг в виде схем.

        Raises:
            NotImplementedError: Если метод не реализован в подклассе.
        """
    
    @classmethod
    @abstractmethod
    async def find_genres(self, query: list[str], engine: RequestManager, base_url: str, parser: BaseParserMother) -> BaseFindEngine:
        """
        Асинхронно выполняет поиск манги по списку жанров.

        Абстрактный метод, который должен быть реализован в подклассах.

        Args:
            query (list[str]): Список жанров для поиска.
            engine (RequestManager): Менеджер для выполнения HTTP-запросов.
            base_url (str): Базовый URL-адрес сайта для парсинга.
            parser (BaseParserMother): Парсер для обработки HTML-разметки.

        Returns:
            list[BaseMangaSchema]: Список найденных манг в виде схем.

        Raises:
            NotImplementedError: Если метод не реализован в подклассе.
        """
    
    async def next_page(self) -> list[BaseMangaSchema]:
        """
        Переходит на следующую страницу результатов поиска.

        Увеличивает номер текущей страницы на 1 и загружает результаты.

        Returns:
            list[BaseMangaSchema]: Список манг с новой страницы.

        See Also:
            select_page: Метод, который выполняет фактический переход на страницу.
        """
        return await self.select_page(self.page_now + 1)
    
    async def back_page(self) -> list[BaseMangaSchema]:
        """
        Возвращается на предыдущую страницу результатов поиска.

        Уменьшает номер текущей страницы на 1 и загружает результаты.

        Returns:
            list[BaseMangaSchema]: Список манг с предыдущей страницы.

        See Also:
            select_page: Метод, который выполняет фактический переход на страницу.
        """
        return await self.select_page(self.page_now - 1)
    
    async def current_page(self) -> list[BaseMangaSchema]:
        """
        Возвращается текущую страницу.

        Returns:
            list[BaseMangaSchema]: Список манг с текущей страницы.

        See Also:
            select_page: Метод, который выполняет фактический переход на страницу.
        """
        return await self.select_page(self.page_now)
    
    async def select_page(self, page: int) -> list[BaseMangaSchema]:
        """
        Переходит на указанную страницу результатов поиска.

        Выполняет HTTP-запрос для получения указанной страницы и парсит результаты.

        Args:
            page (int): Номер страницы для перехода (начинается с 1).

        Returns:
            list[BaseMangaSchema]: Список манг с указанной страницы.

        Raises:
            ValueError: Если номер страницы меньше 1 или больше максимальной страницы.
            ValueError: Если не удалось получить страницу.

        Note:
            Если страница не может быть получена, возвращается пустой список
            и записывается сообщение об ошибке в лог.
        """
        if page < 1:
            logger.warning(
                f"Номер страницы не может быть меньше 1"
            )
            return []
        
        elif page > self.max_page:
            logger.warning(
                f"Количество страниц не может быть больше {self.max_page}"
            )
            return []
            
        await self.update_page(page)
            
        if page in self.cashe:
            logger.info(
                f"Страница {page} уже загружена"
            )
            return self.cashe[page]
        
        if (response := await self.engine.get(self._build_page(), 'read')) is None:
            logger.error(
                "Не удалось получить страницу"
            )
            return []
        
        result = self.parse_page(response)
        self.cashe[page] = result
        
        return result
    
    async def update_page(self, page: int) -> None:
        """
        Обновляет номер текущей страницы.
        """
        
        async with self.lock:
            self.page_now = page

    def parse_page(self, markup: _IncomingMarkup) -> list[BaseMangaSchema]:
        """
        Парсит HTML-разметку страницы результатов поиска.

        Абстрактный метод, который должен быть реализован в подклассах.
        Преобразует полученную разметку в список объектов манги.

        Args:
            markup (_IncomingMarkup): HTML-разметка страницы с результатами поиска.

        Returns:
            list[BaseMangaSchema]: Список распарсенных манг в виде схем.

        Raises:
            NotImplementedError: Если метод не реализован в подклассе.
        """
        return self.parser.parse_page(markup)
    
    @abstractmethod
    def get_max_page(self, markup: _IncomingMarkup) -> int:
        """
        Возвращает максимальное количество страниц результатов поиска.

        Абстрактный метод, который должен быть реализован в подклассах.
        Определяет количество страниц на основе HTML-разметки.
        """
    
    @abstractmethod
    def _build_page(self) -> str:
        """
        Строит URL для запроса указанной страницы результатов.

        Абстрактный метод, который должен быть реализован в подклассах.
        Генерирует полный URL на основе базового адреса и номера страницы.

        Returns:
            str: Полный URL для запроса страницы результатов.

        Raises:
            NotImplementedError: Если метод не реализован в подклассе.
        """
    
    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"page={self.page_now}, "
            f"max_page={self.max_page}, "
            f"loaded={list(self.cashe.keys())}"
        )
    async def all_page(self) -> AsyncGenerator[list[BaseMangaSchema], None]:
        for page in range(1, self.max_page + 1):
            yield await self.select_page(page)