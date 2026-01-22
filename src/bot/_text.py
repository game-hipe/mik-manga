from dataclasses import dataclass
from ..core.entites.schemas import BaseMangaSchema, MangaSchema

@dataclass
class FindText:
    FIND_MANGA_TEXT = (
        "🔍 Я помогу тебе найти мангу по названию или жанрам!.\n"
        "Просто выбери сайт из списка."
    )
    
    FIND_MANGA_TEXT_TEXT = (
        "🔍 Кртуо! Теперь введите название манги! (Минимум 3 буквы)"
    )
    
    FIND_MANGA_GENRES_TEXT = (
        "🔍 Я помогу тебе найти мангу по жанрам!.\n"
        "Просто выбери жанр из списка."
    )
    
    @staticmethod
    def find_manga_result_text(num: int, mangas: list[BaseMangaSchema]) -> str:
        return (
            "🔍 Результаты поиска "
            f"Найдено {num} страниц\n"
            f"{FindText._build_result_text(mangas)}"
        )
    
    @staticmethod
    def _build_result_text(mangas: list[BaseMangaSchema]) -> str:
        text = ""
        for index, manga in enumerate(mangas, 1):
            text += (
                f"{index} "
                f"<b>{manga.title}</b> —— Оригинал <a href={str(manga.url)}>тут</a>\n"
            )
            
        return text


@dataclass
class DownloadText:
    DONWLOAD_MANGA_TEXT = (
        "📥 Я помогу тебе скачать мангу!.\n"
        "Просто пришли мне ссылку!"
    )
        

@dataclass
class Text:
    HELLO_TEXT = (
        "Привет! 👋 Я твой персональный помощник в мире манги.\n"
        "Моя задача — помочь тебе найти самую интересную историю, "
        "объяснить сюжетные повороты или просто порекомендовать шедевр.\n"
        "О чём ты хочешь узнать?"
    )
    
    HELP_TEXT = (
        "Руководство, по боту.\n"
        "/download - <b>Скачать мангу</b>\n"
        "/find - <b>Поиск манги</b>\n"
        "/help - <b>Помощь</b>"
        "/start - <b>Начать</b>"
    )
    
    @staticmethod
    def show_manga_text(manga: MangaSchema) -> str:
        if not isinstance(manga, MangaSchema):
            raise TypeError(
                f"Ошибка show_manga_text, получила {type(manga)}"
            )
        
        return (
            f"📖 <b>{manga.title}</b>\n\n"
            f"Жанры: {' | '.join(f"<b>{x}</b>" for x in manga.genres)}\n"
            f"Автор: <b>{manga.author}</b>\n"
            f"Язык: <b>{manga.language}</b>\n"
            f"Количество актов: {len(manga.chapters)}\n"
            f'Оригинал: <a href="{str(manga.url)}">тут</a>'
        )