from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher

from ..shared import config
from ..core.service.message import TextGenerator


async def get_bot(
    text_api: TextGenerator, token: str | None = None
) -> tuple[Bot, Dispatcher]:
    token = token or config.telegram

    storage = MemoryStorage()
    bot = Bot(token)
    dp = Dispatcher(storage=storage)

    return bot, dp


async def start_bot(text_api: TextGenerator, token: str | None = None):
    bot, dp = await get_bot(token)

    await dp.start_polling(bot)
