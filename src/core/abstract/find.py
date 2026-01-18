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

from abc import ABC, abstractmethod

from bs4 import _IncomingMarkup
from loguru import logger

from ..manager.request import RequestManager
from ..entites.schemas import BaseMangaSchema


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
    BASE_FEATURES: str = "html.parser"
    """Базовый движок для парсинга (например, 'html.parser', 'lxml', и т.д.)."""
    
    def __init__(
        self,
        engine: RequestManager,
        base_url: str,
        features: str | None = BASE_FEATURES
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
        self.engine = engine
        self.base_url = base_url
        self.features = features or self.BASE_FEATURES
        
        self.page_now = 1
        self.max_page = -1
    
    @classmethod
    @abstractmethod
    async def find(cls, query: str):
        """
        Асинхронно выполняет поиск манги по текстовому запросу.

        Абстрактный метод, который должен быть реализован в подклассах.

        Args:
            query (str): Поисковый запрос (название манги или ключевые слова).

        Returns:
            list[BaseMangaSchema]: Список найденных манг в виде схем.

        Raises:
            NotImplementedError: Если метод не реализован в подклассе.
        """
        ...
    
    @classmethod
    @abstractmethod
    async def find_genres(self, genres: list[str]):
        """
        Асинхронно выполняет поиск манги по списку жанров.

        Абстрактный метод, который должен быть реализован в подклассах.

        Args:
            genres (list[str]): Список жанров для поиска.

        Returns:
            list[BaseMangaSchema]: Список найденных манг в виде схем.

        Raises:
            NotImplementedError: Если метод не реализован в подклассе.
        """
        ...
    
    async def next_page(self) -> list[BaseMangaSchema]:
        """
        Переходит на следующую страницу результатов поиска.

        Увеличивает номер текущей страницы на 1 и загружает результаты.

        Returns:
            list[BaseMangaSchema]: Список манг с новой страницы.

        See Also:
            select_page: Метод, который выполняет фактический переход на страницу.
        """
        await self.select_page(self.page_now + 1)
    
    async def back_page(self) -> list[BaseMangaSchema]:
        """
        Возвращается на предыдущую страницу результатов поиска.

        Уменьшает номер текущей страницы на 1 и загружает результаты.

        Returns:
            list[BaseMangaSchema]: Список манг с предыдущей страницы.

        See Also:
            select_page: Метод, который выполняет фактический переход на страницу.
        """
        await self.select_page(self.page_now - 1)
    
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
            raise ValueError(
                "Количество страниц не может быть меньше 1"
            )
        elif page > self.max_page:
            raise ValueError(
                f"Количество страниц не может быть больше {self.max_page}"
            )
        
        if (response := await self.engine.get(self._build_page(), 'read')) is None:
            logger.error(
                "Не удалось получить страницу"
            )
            return []
            
        return self.parse_page(response)
    
    @abstractmethod
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
        ...
    
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
        ...
        ...