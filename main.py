import asyncio

import aiohttp

from src.spider.multi_manga.spider import MultiMangaSpider

async def main():
    async with aiohttp.ClientSession() as session:
        api = MultiMangaSpider(session)
        await api.get_manga(
            "https://multi-manga.today/16092-nacuki-natsuki.html"
        )
        
        
    

asyncio.run(main())