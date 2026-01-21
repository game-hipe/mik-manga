"""Гнениерирует сообщение для ответа."""

import random
import json

from urllib.parse import urlparse
from pathlib import Path

from httpx import AsyncClient
from google import genai

from ..entites.schemas import BaseMangaSchema
from ...shared import config


class TextGenerator:
    BASE_MODEL: str = "gemini-2.5-flash"  # Рекомендую использовать актуальные модели
    BASE_LANGUAGE: str = "ru"
    BASE_MARKUP: str = "HTML"
    BASE_FILE_ANSWER: str = Path(__file__).parent / "offline-answer.json"

    NEW_MANGA_TEXT: str = (
        "Ты — помощник администратора сайта манги. Твоя задача — создавать информирующие и привлекательные анонсы о новых поступлениях для публикации в Telegram-канале.\n"
        "\n"
        "### ЗАДАЧА:\n"
        "Сгенерируй отдельные сообщения о новых мангах, добавленных на сайт. Каждое сообщение должно быть самостоятельным постом.\n"
        "\n"
        "### ВХОДНЫЕ ДАННЫЕ (контекст):\n"
        "1.  **Количество сообщений:** {count}. Сгенерируй ровно столько сообщений, сколько указано в этом параметре.\n"
        "2.  **Язык сообщений:** {language}.\n"
        "3.  **Поддержка разметки:** {markup}. Используй **ТОЛЬКО** следующие теги, доступные в Telegram:\n"
        "    *   `<b>` / `</b>` — Жирный текст.\n"
        "    *   `<i>` / `</i>` — Курсив.\n"
        "    *   `<u>` / `</u>` — Подчеркнутый текст.\n"
        "    *   `<s>` / `</s>` — Зачеркнутый текст.\n"
        "    *   `<tg-spoiler>` / `</tg-spoiler>` — Скрытый текст (спойлер).\n"
        "    *   `<code>` / `</code>` — Моноширинный шрифт (для кода).\n"
        "    *   `<pre>` / `</pre>` — Предварительно отформатированный текст.\n"
        '    *   `<a href="...">` / `</a>` — Гиперссылка.\n'
        "    *   **Запрещены:** `#`, `*`, `_`, `~`, ```` для форматирования.\n"
        "\n"
        "### ТРЕБОВАНИЯ К ФОРМАТУ ОТВЕТА:\n"
        "*   Сгенерируй ровно {count} сообщений.\n"
        "*   Разделяй каждое сообщение символом вертикальной черты `|`.\n"
        "*   Формат итогового вывода: `[Сообщение_1]|[Сообщение_2]|[Сообщение_3]|...`\n"
        "*   **Важно:** Внутри самих сообщений символ `|` использовать нельзя.\n"
        "\n"
        "### СТРУКТУРА И СТИЛЬ КАЖДОГО СООБЩЕНИЯ:\n"
        "1.  **Заголовок:** Используй `<b>` для названия манги.\n"
        "2.  **Описание:** Кратко (1-3 предложения) опиши сюжет или концепцию. Используй `<i>` для выделения ключевых моментов или атмосферы.\n"
        "3.  **Детали:** Укажи жанр из данных или создай подходящий.\n"
        '4.  **Призыв к действию (CTA):** Добавь ссылку на сайт, используя тег `<a href="[ссылка_из_данных]">Читать на сайте</a>`.\n'
        "5.  **Общий тон:** Официально-дружелюбный, побуждающий к интересу.\n"
        "\n"
        "### ДАННЫЕ ДЛЯ ГЕНЕРАЦИИ:\n"
        "Тебе будут предоставлены данные о мангах в следующем формате (каждая манга — отдельный объект):\n"
        "['Название манги: TITLE, URL: URL', 'Название манги: TITLE, URL: URL']"
        "\n"
        "### ПРИМЕР:\n"
        "Для count=2, language=Russian, markup=HTML и данных:\n"
        "['Название манги: Мой братик больше не братик!, URL: https://example.com', 'Название манги: Исекай с 10 красотакми?!?!, URL: https://example.com/1']"
        "\n"
        "Твой вывод должен быть:\n"
        "<b>Мой братик больше не братик!</b>\n"
        "<i>>Вы когда нибудь задумывались что будет если превратится в мальчика? Вот и не стоит!</i>\n"
        '<a href="https://example.com">Читать на сайте</a>'
        "|"
        "<b>Исекай с 10 красотакми?!?!</b>\n"
        "<i>Исекай это уже трудно, но выжить с 10 красотками? Это же мечта!</i>\n"
        '<a href="https://example.com/1">Читать на сайте</a>\n'
        "\n"
        "### ФАКТИЧЕСКИЕ ДАННЫЕ:\n"
        "{data}"
    )

    OFFLINE_TEXT: str = "Найдена новая манга, количество манг {count}"

    def __init__(
        self,
        session: AsyncClient | None = None,
        api_key: str | None = None,
        model: str | None = None,
        language: str | None = None,
        markup: str | None = None,
    ):
        api_key = api_key or config.gemini_api
        self.use_client = bool(api_key)

        if api_key:
            self.client = genai.Client(
                api_key=api_key,
                http_options={"api_version": "v1beta", "httpx_async_client": session},
            )

        self.markup = markup or self.BASE_MARKUP
        self.language = language or self.BASE_LANGUAGE
        self.model = model or self.BASE_MODEL

        with open(self.BASE_FILE_ANSWER, encoding="utf-8") as f:
            self.answers = json.load(f)

    async def generate_manga_message(self, mangas: list[BaseMangaSchema]) -> list[str]:
        """Пример асинхронной генерации текста"""
        if not self.use_client:
            return self.create_offline_answer(mangas)

        data = [f"Название манги: {x.title}, URL: {x.url}" for x in mangas]
        prompt = self.NEW_MANGA_TEXT.format(
            count=len(mangas),
            language=self.language,
            markup=self.markup,
            data="\n".join(data),
        )

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model, contents=prompt
            )
            return response.text.split("|")[:3]
        except Exception:
            return self.create_offline_answer(mangas)

    def create_offline_answer(self, mangas: list[BaseMangaSchema]) -> str:
        final_text = ""
        text: dict[str, str] = random.choice(self.answers)

        final_text += (text["title"].strip() + "\n").format(count=len(mangas))

        for indx, line in enumerate(mangas[:5], 1):
            final_text += (f"{indx}. " + text["content"].strip() + "\n").format(
                title=line.title, url=str(line.url)
            )

        final_text += f"\n\nБольше тут → <a href=https://{urlparse(str(mangas[0].url)).netloc}>Тут</a>"

        return final_text
