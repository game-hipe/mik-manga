import asyncio

from loguru import logger

async def main():
    print("Hello World!") # Тут будет запуск

if __name__ == "__main__":
    try:
        asyncio.run(main())
        
    except KeyboardInterrupt:
        logger.info("Завершение работы...")
        
    except Exception as e:
        logger.critical(e)
        
    finally:
        logger.info("Завершение работы...")