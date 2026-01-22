from typing import TypedDict, Unpack

from pydantic import BaseModel, ConfigDict
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from ..shared import config
from ..core.service.message import TextGenerator
from ..core.service.manga import MangaService
from .handlers import CommandHandlers

class TypedBotConfig(TypedDict):
    text_api: TextGenerator
    manga_api: MangaService
    token: str | None = None

class BotConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    text_api: TextGenerator
    manga_api: MangaService
    token: str | None = None

async def get_bot(**kwargs: Unpack[TypedBotConfig]) -> tuple[Bot, Dispatcher]:
    bot_config = BotConfig(**kwargs)
    token = bot_config.token or config.telegram

    handlers = CommandHandlers(bot_config.text_api, bot_config.manga_api)
    storage = MemoryStorage()
    bot = Bot(token, default=DefaultBotProperties(parse_mode = "HTML"))
    dp = Dispatcher(storage=storage)

    dp.include_router(handlers.router)
    
    return bot, dp

async def start_bot(**kwargs: Unpack[TypedBotConfig]):
    bot, dp = await get_bot(**kwargs)
    
    await dp.start_polling(bot)