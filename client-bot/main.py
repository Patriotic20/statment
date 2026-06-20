import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import settings
from handlers.start import router as start_router
from handlers.issues import router as issues_router

async def main():
    # Настройка базового логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    
    # Инициализация бота и диспетчера (Router)
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрация роутеров с обработчиками
    dp.include_router(start_router)
    dp.include_router(issues_router)

    # Пропуск накопившихся апдейтов (опционально)
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запуск процесса polling
    logging.info("Starting Telegram Bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
