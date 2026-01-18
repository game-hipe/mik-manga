from abc import ABC, abstractmethod

from bs4 import BeautifulSoup, _IncomingMarkup


class BaseMangaParser(ABC):
    def __init__(self, base_url: str, features: str = 'html.parser'):
        self.base_url = base_url
        self.features = features
        
    def extract_manga(self, markup: _IncomingMarkup):
        soup = self.build_soup()
        
        title = self._extract_title()
        
    def _extract_title(self, soup: BeautifulSoup) -> str:
        ...
        
    def _extract_poster(self, soup: BeautifulSoup) -> str:
        ...
        
    def build_soup(self, markup: _IncomingMarkup, features: str | None = None):
        return BeautifulSoup(
            markup = markup,
            features = features or self.features
        )