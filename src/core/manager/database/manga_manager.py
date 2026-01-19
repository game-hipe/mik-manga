from typing import TypeVar
from hashlib import sha256

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, AsyncSession
from sqlalchemy.sql._typing import _TypedColumnClauseArgument
from loguru import logger

from ...entites.models import Manga, Language, Author, Genre, GenreManga, Chapter
from ...entites.schemas import MangaDetailSchema, MangaOutputSchema, ChapterSchema

T = TypeVar("T")


class MangaManager:
    def __init__(self, engine: AsyncEngine):
        self.engine = engine
        self.Session: async_sessionmaker[AsyncSession] = async_sessionmaker(self.engine)

    async def add_manga(self, manga: MangaDetailSchema) -> MangaOutputSchema:
        async with self.Session() as session:
            async with session.begin():
                author = await self._add_author(manga.author)
                language = await self._add_language(manga.language)

                _manga = Manga(
                    title=manga.title,
                    origninal_url=manga.url,
                    poster=str(manga.poster),
                    author_id=author.id,
                    language_id=language.id,
                )
                session.add(_manga)
                await session.flush()

                await self._connect(manga.genres, manga.chapters, _manga)

            return MangaOutputSchema(
                title=manga.title,
                poster=manga.poster,
                url=manga.url,
                genres=manga.genres,
                author=manga.author,
                language=manga.language,
                chapters=manga.chapters,
                id=_manga.id,
            )

    async def get_manga(self, id: int) -> MangaOutputSchema:
        async with self.Session() as session:
            manga = await session.get(Manga, id)
            if manga is None:
                logger.warning(f"Манга под ID {id} не обнаружен")
                return

    async def _connect(
        self, genres_titles: list[str], chapters: list[ChapterSchema], manga: Manga
    ) -> None:
        async with self.Session() as session:
            async with session.begin():
                for title in genres_titles:
                    genre = await self._add_genre(title)
                    session.add(GenreManga(manga_id=manga.id, genre_id=genre.id))

                for chapter in chapters:
                    sku = sha256(str(chapter.gallery[0]).encode()).hexdigest()[:32]
                    session.add(
                        Chapter(gallery=chapter.gallery, manga_id=manga.id, sku=sku)
                    )

    async def _add_genre(self, title: str) -> Genre:
        return self._add_item(title, Genre)

    async def _add_author(self, title: str) -> Author:
        return self._add_item(title, Author)

    async def _add_language(self, title: str) -> Language:
        return self._add_item(title, Language)

    async def _add_item(self, title: str, factory: _TypedColumnClauseArgument[T]) -> T:
        async with self.Session() as session:
            async with session.begin():
                item = await session.scalar(select(factory).where(T.title == title))
                if item:
                    logger.debug("Обнаружен обьект в БД (title)")
                    return item

                item = factory(title=title)

                session.add(item)
                await session.flush()

                return item

    async def build_manga(self, manga: Manga) -> MangaOutputSchema:
        return MangaOutputSchema(
            title=manga.title,
            poster=manga.poster,
            url=manga.original_url,
            genres=manga.genres,
            author=manga.author,
            language=manga.language,
            chapters=manga.chapters,
            id=manga.id,
        )
