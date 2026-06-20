import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import settings
from consumer import start_consumer
from handlers.start import router as start_router
from handlers.issues import router as issues_router


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(start_router)
    dp.include_router(issues_router)

    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Starting Worker Bot...")

    await asyncio.gather(
        start_consumer(bot),
        dp.start_polling(bot),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Worker bot stopped by user")
