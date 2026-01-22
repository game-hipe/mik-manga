import asyncio
import random

from aiohttp import ClientSession
from loguru import logger

from src.core.service.message import TextGenerator
from src.core.service.manga import MangaService
from src.bot import start_bot

from src.spider import MultiManga

async def main():
    async with ClientSession() as session:
        
        text_api = TextGenerator()
        manga_service = MangaService(
            session,
            spiders = [MultiManga]
        )
        
        await start_bot(
            text_api = text_api,
            manga_api = manga_service
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
        
    except KeyboardInterrupt:
        logger.info("Пользователь приостоновил работу программы...")
        
    except Exception as e:
        logger.critical(e)
        
    finally:
        logger.info("Завершение работы...")