import asyncio

import aiohttp


async def main():
    async with aiohttp.ClientSession() as session:  # noqa
        print("FuckWorld!")


asyncio.run(main())
