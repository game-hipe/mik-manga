from urllib.parse import urlparse

from aiogram import Router, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from ...core.service.message import TextGenerator
from ...core.service.manga import MangaService
from .._text import Text, FindText
from .._state import GetManga


class CommandHandlers:
    def __init__(self, text_api: TextGenerator, manga_api: MangaService):
        self.text_api = text_api
        self.manga_api = manga_api
        self.router = Router()

        self._setup_handlers()

    def _setup_handlers(self):
        self.router.message.register(self.start_handler, Command("start"))
        self.router.message.register(self.help_handler, Command("help"))
        self.router.message.register(self.find_handler, Command("find"))
        
        self.router.message.register(self.cancel, Command("cancel"))
        self.router.callback_query.register(self.cancel, F.data == 'cancel')

        self.router.callback_query.register(self.selected_site, F.data.startswith('find:'))
        
        self.router.callback_query.register(self.search_by_genres, F.data.startswith('genres:'))
        self.router.callback_query.register(self.search_by_name, F.data.startswith('name:'))
        self.router.callback_query.register(self._update_genres, F.data.startswith('genre:'))
        
    async def start_handler(self, message: Message):
        await message.answer(
            Text.HELLO_TEXT
        )
        
    async def help_handler(self, message: Message):
        await message.answer(
            Text.HELP_TEXT
        )
        
    async def find_handler(self, message: Message):
        await message.answer(
            FindText.FIND_MANGA_TEXT,
            reply_markup = self._build_find_keyboard()
        )
        
    async def cancel(self, message: Message | CallbackQuery, state: FSMContext):
        if isinstance(message, Message):
            await state.clear()
            await message.delete()
            await message.answer(
                "Состояние сброшено."
            )
        else:
            await state.clear()
            await message.message.delete()
            await message.message.answer(
                "Состояние сброшено."
            )
    
    async def selected_site(self, call: CallbackQuery):
        spider = self.manga_api.get_by_id(
            self.get_spider_id(call.data)
        )
        if spider is None:
            await call.message.answer("Не удалось получит паука! Попробуйте сделать это позже")
            return

        await call.message.edit_text(
            "Хорошо! Теперь выберите каким образом будем искать мангу!",
            reply_markup = InlineKeyboardMarkup(
                inline_keyboard = [
                    [
                        InlineKeyboardButton(text = 'По названию', callback_data = "name:" + call.data),
                        InlineKeyboardButton(text = 'По жанрам', callback_data = "genres:" + call.data)
                    ]
                ]
            )
        )
    
    async def search_by_genres(self, call: CallbackQuery):
        spider = self.manga_api.get_by_id(
            self.get_spider_id(call.data)
        )
        if spider is None:
            await call.message.answer("Не удалось получит паука! Попробуйте сделать это позже")
            return
        
        genres = await spider.get_genres()
        keyborad = [
            [
                InlineKeyboardButton(text=genre, callback_data=f"genre:{genre}:"+call.data) for genre in genres[i:i+4]
            ] for i in range(0, len(genres[:20]), 4)
        ]
        keyborad.append(
            [
                InlineKeyboardButton(text="Поиск", callback_data="search:" + call.data),
                InlineKeyboardButton(text="Отмена", callback_data="cancel")
            ]
        )
        
        await call.message.edit_text(
            FindText.FIND_MANGA_GENRES_TEXT,
            reply_markup = InlineKeyboardMarkup(inline_keyboard = keyborad)
        )
        
    async def _update_genres(self, call: CallbackQuery):
        for keyboard in call.message.reply_markup.inline_keyboard:
            for button in keyboard:
                if button.callback_data == call.data:
                    if "✅" in button.text:
                        button.text = button.text.replace("✅ ", "")
                    else:
                        button.text = "✅ " + button.text
        await call.message.edit_reply_markup(
            reply_markup = call.message.reply_markup
        )
        
    async def search_by_name(self, call: CallbackQuery, state: FSMContext):
        state.set_state(GetManga.waiting_for_title)
        await call.message.edit_text(
            FindText.FIND_MANGA_TEXT_TEXT
        )
        
    async def get_name(self, message: Message, state: FSMContext):
        ...
    
    @staticmethod
    def get_spider_id(data: str):
        return data.split(":")[-1]    

    def _build_find_keyboard(self):
        """Создает клавиатуру для выбора источника поиска манги."""
        
        sources = {}
        for spider in self.manga_api.loaded_spiders:
            domain = urlparse(spider.BASE_URL).netloc
            spider_id = spider.__class__.__name__.lower()
            
            if spider_id not in sources:
                sources[spider_id] = {
                    'domain': domain,
                    'spider_name': spider.__class__.__name__,
                    'display_name': domain.replace('www.', '')
                }

        buttons = []
        for spider_id, data in sources.items():
            button = InlineKeyboardButton(
                text=data['display_name'],
                callback_data=f"find:{spider_id}"
            )
            buttons.append(button)

        keyboard = []
        for i in range(0, len(buttons), 2):
            row = buttons[i:i+2]
            keyboard.append(row)
            
        keyboard.append(
            [InlineKeyboardButton(text="Отмена", callback_data="cancel")]
        )
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)