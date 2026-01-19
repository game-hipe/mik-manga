from urllib.parse import urljoin
from abc import ABC, abstractmethod
from typing import Type

from bs4 import BeautifulSoup, Tag, _IncomingMarkup

from ..entites.schemas import MangaSchema, BaseMangaSchema, ChapterSchema


__all__ = ["BaseMangaParser", "BasePageParser"]


class BaseParser(ABC):
    def __init__(self, base_url: str, features: str = "html.parser"):
        self.base_url = base_url
        self.features = features

    def build_soup(self, markup: _IncomingMarkup, features: str | None = None):
        return BeautifulSoup(markup=markup, features=features or self.features)

    def urljoin(self, url: str):
        if url.startswith("http"):
            return url
        else:
            return urljoin(self.base_url, url)


class BaseMangaParser(BaseParser):
    def extract_manga(self, markup: _IncomingMarkup) -> MangaSchema:
        soup = self.build_soup(markup)

        title = self._extract_title(soup)
        poster = self._extract_poster(soup)
        url = self._extract_url(soup)
        genres = self._extract_genres(soup)
        author = self._extract_author(soup)
        language = self._extract_language(soup)
        chapters = self._extract_chapters(soup)

        return MangaSchema(
            title=title,
            poster=poster,
            url=url,
            genres=genres,
            author=author,
            language=language,
            chapters=chapters,
        )

    @abstractmethod
    def _extract_title(self, soup: BeautifulSoup) -> str: ...

    @abstractmethod
    def _extract_poster(self, soup: BeautifulSoup) -> str: ...

    @abstractmethod
    def _extract_url(self, soup: BeautifulSoup) -> str: ...

    @abstractmethod
    def _extract_genres(self, soup: BeautifulSoup) -> list[str]: ...

    @abstractmethod
    def _extract_author(self, soup: BeautifulSoup) -> str | None: ...

    @abstractmethod
    def _extract_language(self, soup: BeautifulSoup) -> str | None: ...

    @abstractmethod
    def _extract_chapters(self, soup: BeautifulSoup) -> list[str]: ...


class BasePageParser(BaseParser):
    def extract_page(self, markup: _IncomingMarkup) -> list[BaseMangaSchema]:
        soup = self.build_soup(markup)

        return [self._make_manga(tag) for tag in self._select_all(soup)]

    @abstractmethod
    def _select_all(self, soup: BeautifulSoup) -> list[Tag]: ...

    @abstractmethod
    def _make_manga(self, tag: Tag) -> BaseMangaSchema: ...


class BaseChapterParser(BaseParser):
    @abstractmethod
    def extract_chapter(self, markup: _IncomingMarkup, url: str) -> ChapterSchema: ...


class BaseParserMother(BaseParser):
    MANGA_PARSER: Type[BaseMangaParser]
    PAGE_PARSER: Type[BasePageParser]
    CHAPTER_PARSER: Type[BaseChapterParser]

    def __init__(
        self,
        base_url,
        features="html.parser",
    ):
        super().__init__(base_url, features)

        if not issubclass(self.MANGA_PARSER, BaseMangaParser):
            raise TypeError(
                f"{type(self.MANGA_PARSER)} Не наследуется от BaseMangaParser"
            )

        if not issubclass(self.PAGE_PARSER, BasePageParser):
            raise TypeError(
                f"{type(self.PAGE_PARSER)} Не наследуется от BasePageParser"
            )

        if not issubclass(self.CHAPTER_PARSER, BaseChapterParser):
            raise TypeError(
                f"{type(self.CHAPTER_PARSER)} Не наследуется от BaseChapterParser"
            )

        self.manga_parser: BaseMangaParser = self.MANGA_PARSER(
            base_url=base_url, features=features
        )

        self.page_parser: BasePageParser = self.PAGE_PARSER(
            base_url=base_url, features=features
        )

        self.chapter_parser: BaseChapterParser = self.CHAPTER_PARSER(
            base_url=base_url, features=features
        )

    def parse_manga(self, markup: _IncomingMarkup) -> MangaSchema:
        return self.manga_parser.extract_manga(markup)

    def parse_page(self, markup: _IncomingMarkup) -> list[BaseMangaSchema]:
        return self.page_parser.extract_page(markup)

    def parse_chapter(self, markup: _IncomingMarkup, url: str) -> ChapterSchema:
        return self.chapter_parser.extract_chapter(markup, url)
