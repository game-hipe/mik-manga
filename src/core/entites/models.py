"""Хранит модели для работы с базой данных.

Модуль определяет структуру таблиц в базе данных с использованием SQLAlchemy ORM.
Каждый класс представляет собой таблицу в базе данных и содержит поля,
соответствующие столбцам, а также связи с другими таблицами.
"""

from typing import List

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, JSON


__all__ = [
    "Base",
    "Genre",
    "Author",
    "Language",
    "Chapter",
    "Manga",
    "GenreManga"
]


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy."""
    pass


class Genre(Base):
    """Модель жанра манги.
    
    Attributes:
        id: Уникальный идентификатор жанра.
        title: Название жанра.
        manga_list: Список связанных манг через промежуточную таблицу.
    """
    
    __tablename__ = "genres"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    
    manga_list: Mapped[List["GenreManga"]] = relationship(
        "GenreManga",
        back_populates="genre"
    )


class Author(Base):
    """Модель автора манги.
    
    Attributes:
        id: Уникальный идентификатор автора.
        title: Имя автора.
        manga: Список манг, созданных автором.
    """
    
    __tablename__ = "authors"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    
    manga: Mapped[List["Manga"]] = relationship(
        "Manga",
        back_populates="author"
    )


class Language(Base):
    """Модель языка перевода манги.
    
    Attributes:
        id: Уникальный идентификатор языка.
        title: Название языка.
        manga: Список манг на этом языке.
    """
    
    __tablename__ = "languages"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    
    manga: Mapped[List["Manga"]] = relationship(
        "Manga",
        back_populates="language"
    )


class Chapter(Base):
    """Модель для таблицы глав манги.

    Представляет таблицу 'chapters', хранящую информацию о главах манги,
    включая список изображений (галерею) и связь с конкретной мангой.
    
    Attributes:
        id: Уникальный идентификатор главы.
        gallery: Список ссылок на изображения главы.
        manga_id: Идентификатор манги, к которой принадлежит глава.
        manga: Манга, к которой принадлежит данная глава.
        sku: Уникальный ID, создаётся на основе 1 URL из gallery
    """
    __tablename__ = "chapters"

    id: Mapped[int] = mapped_column(primary_key = True)
    """Идентификатор главы (первичный ключ)."""

    gallery: Mapped[list[str]] = mapped_column(JSON())
    """Список ссылок на изображения главы.

    Хранится в формате JSON как массив строк (URL изображений).
    """

    manga_id: Mapped[int] = mapped_column(ForeignKey("mangas.id"))
    """Внешний ключ, ссылающийся на идентификатор манги."""

    manga: Mapped["Manga"] = relationship(
        "Manga",
        back_populates="chapters"
    )
    """Связь с моделью Manga.

    Позволяет получить мангу, к которой принадлежит данная глава.
    """
    sku: Mapped[str] = mapped_column(String(32), unique = True)
    """Уникальный ID, создаётся на основе 1 URL из gallery"""


class Manga(Base):
    """Модель манги.
    
    Attributes:
        id: Уникальный идентификатор манги.
        title: Название манги.
        original_url: Оригинальная ссылка на мангу.
        poster: Ссылка на постер манги.
        author_id: Идентификатор автора.
        language_id: Идентификатор языка.
        genre_links: Связи с жанрами через промежуточную таблицу.
        language: Язык перевода манги.
        author: Автор манги.
        chapers: Список глав манги.
    """
    
    __tablename__ = "mangas"
    
    id: Mapped[int] = mapped_column(primary_key = True)
    title: Mapped[str] = mapped_column(String(255))
    original_url: Mapped[str] = mapped_column(String(2048))
    poster: Mapped[str] = mapped_column(String(2048))
    
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    language_id: Mapped[int] = mapped_column(ForeignKey("languages.id"))
    
    genre_links: Mapped[List["GenreManga"]] = relationship(
        "GenreManga",
        back_populates="manga"
    )
    
    language: Mapped["Language"] = relationship(
        "Language",
        back_populates="manga"
    )
    
    author: Mapped["Author"] = relationship(
        "Author",
        back_populates="manga"
    )
    
    chapters: Mapped[List["Chapter"]] = relationship(
        "Chapter",
        back_populates="manga"
    )
    
    @property
    def genres(self) -> List["Genre"]:
        """Получить список жанров манги.
        
        Returns:
            Список объектов Genre, связанных с мангой.
        """
        return [link.genre for link in self.genre_links]


class GenreManga(Base):
    """Промежуточная таблица для связи многие-ко-многим между мангой и жанрами.
    
    Attributes:
        id: Уникальный идентификатор связи.
        manga_id: Идентификатор манги.
        genre_id: Идентификатор жанра.
        manga: Связанная манга.
        genre: Связанный жанр.
    """
    
    __tablename__ = "genres_manga"
    
    id: Mapped[int] = mapped_column(primary_key = True)
    manga_id: Mapped[int] = mapped_column(ForeignKey("mangas.id"))
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id"))
    
    manga: Mapped["Manga"] = relationship(
        "Manga",
        back_populates="genre_links"
    )
    
    genre: Mapped["Genre"] = relationship(
        "Genre",
        back_populates="manga_list"
    )