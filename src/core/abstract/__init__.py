"""Хранит абстактные классы"""

from .find import BaseFindEngine
from .spider import BaseSpider
from .parser import BasePageParser, BaseParserMother, BaseMangaParser, BaseChapterParser


__all__ = [
    "BaseFindEngine",
    "BaseSpider",
    "BaseParserMother",
    "BasePageParser",
    "BaseMangaParser",
    "BaseChapterParser",
]
