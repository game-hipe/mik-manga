"""Хранит схемы для хранение данных

Модуль, помогает для хранения данных.
"""

from pydantic import BaseModel, HttpUrl, Field
from aiohttp import BasicAuth


__all__ = [
    "ChapterSchema",
    "BaseMangaSchema",
    "MangaSchema",
    "MangaDetailSchema",
    "MangaOutputSchema",
    "ProxySchema",
]


class ChapterSchema(BaseModel):
    """
    Схема данных для главы манги.

    Args:
        url (HttpUrl): URL адрес на главу
        gallery (list[HttpUrl]): Список URL-адресов изображений в главе.
    """

    url: HttpUrl
    gallery: list[HttpUrl]


class BaseMangaSchema(BaseModel):
    """
    Базовая схема данных для манги.

    Args:
        title (str): Название манги.
        poster (HttpUrl): URL-адрес постера (обложки) манги.
        url (HttpUrl): URL-адрес страницы манги.
    """

    title: str
    poster: HttpUrl
    url: HttpUrl


class MangaSchema(BaseMangaSchema):
    """
    Схема данных для манги с дополнительной информацией.

    Наследует BaseMangaSchema

    Args:
        genres (list[str]): Список жанров манги.
        author (str): Имя автора манги.
        language (str): Язык перевода манги.
        chapters (list[str]): Список ссылок на главы манги.
    """

    genres: list[str]
    author: str
    language: str
    chapters: list[HttpUrl]


class MangaDetailSchema(MangaSchema):
    """
    Схема данных для подробной информации о манге.

    Переопределяет поле chapters, заменяя список строк на список объектов ChapterSchema.

    Args:
        chapters (list[ChapterSchema]): Список объектов, каждый из которых содержит галерею изображений главы.
    """

    chapters: list[ChapterSchema]


class MangaOutputSchema(MangaDetailSchema):
    """
    Схема данных для вывода информации о манге с уникальным идентификатором.

    Добавляет идентификатор записи в системе.

    Args:
        id (int): Уникальный идентификатор манги в базе данных или приложении.
    """

    id: int


class ProxySchema(BaseModel):
    """
    Схема данных для настройки прокси-сервера с аутентификацией

    Args:
        proxy (str): ip адрес сервера
        login (str | None): логин для авторизации
        password (str | None): пароль для авторизации
    """

    proxy: str
    login: str | None = Field(default=None)
    password: str | None = Field(default=None)

    def auth(self) -> dict[str, str | BasicAuth]:
        return {
            "proxy": self.proxy,
            "proxy_auth": BasicAuth(login=self.login, password=self.password or "")
            if self.login
            else None,
        }
