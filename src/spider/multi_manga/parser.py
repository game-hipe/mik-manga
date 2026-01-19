from bs4 import BeautifulSoup
from functools import lru_cache

from ...core.abstract.parser import (
    BaseMangaParser,
    BasePageParser,
    BaseChapterParser,
    BaseParserMother,
)
from ...shared import MissingRequiredAttributeError
from ...core.entites.schemas import BaseMangaSchema, ChapterSchema


class MultiMangaParser(BaseMangaParser):
    def _extract_title(self, soup):
        if title := soup.select_one("div#info h1"):
            return title.get_text(strip=True)
        raise MissingRequiredAttributeError("Название не найдено")

    def _extract_poster(self, soup):
        if poster := soup.select_one("div#cover img"):
            if "data-src" not in poster.attrs:
                raise MissingRequiredAttributeError("Постер не найден")

            return self.urljoin(poster["data-src"])

        raise MissingRequiredAttributeError("Постер не найден")

    def _extract_url(self, soup):
        if url := soup.select_one('link[rel="canonical"]'):
            if "href" not in url.attrs:
                raise MissingRequiredAttributeError("Ссылка не найдена")
            return self.urljoin(url["href"])
        raise MissingRequiredAttributeError("Ссылка не найдена")

    def _extract_genres(self, soup):
        return self._extract_tags(soup).get("Теги", [])

    def _extract_author(self, soup):
        return self._extract_tags(soup).get("Автор", [None])[0]

    def _extract_language(self, soup):
        return self._extract_tags(soup).get("Язык", [None])[0]

    @lru_cache(1)
    def _extract_tags(self, soup: BeautifulSoup) -> dict[str, list[str]]:
        result = {}
        for container in soup.select("section#tags div.tag-container"):
            if not container.next_element:
                continue

            tag_name = container.next_element.get_text(strip=True)
            result[tag_name] = [
                tag.get_text(strip=True) for tag in container.select("a.tag")
            ]

        return result

    def _extract_chapters(
        self, soup
    ):  # NOTE: Мы возращаем самого себя, так-как изображение уже находятся в soup, но для совместимости идём на костыли
        return [self._extract_url(soup)]


class MultiMangaPageParser(BasePageParser):
    def _select_all(self, soup):
        return soup.select("div.container.index-container div#dle-content div.gallery")

    def _make_manga(self, tag):
        a = tag.select_one("a")
        img = tag.select_one("img")
        title = tag.get_text(strip=True)

        if all([a, img, title]):
            return BaseMangaSchema(
                title=title,
                poster=self.urljoin(img.get("src", img["data-src"])),
                url=self.urljoin(a["href"]),
            )
        raise MissingRequiredAttributeError("Не удалось извлечь мангу")


class MultiMangaChapterParser(BaseChapterParser):
    def extract_chapter(self, markup, url):
        result = []
        soup = self.build_soup(markup)

        for img in soup.select("div#thumbnail-container div.thumb-container img"):
            result.append(self.urljoin(img["data-src"]))
        return ChapterSchema(url=url, gallery=result)


class MultiMangaParserMother(BaseParserMother):
    MANGA_PARSER = MultiMangaParser
    PAGE_PARSER = MultiMangaPageParser
    CHAPTER_PARSER = MultiMangaChapterParser
