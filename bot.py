import asyncio
from aiogram import Bot, Dispatcher
from config import API_TOKEN
from database import init_db
from handlers import start, language, level, lessons, register, topics

async def main():
    await init_db()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(register.router)
    dp.include_router(language.router)
    dp.include_router(level.router)
    dp.include_router(lessons.router)
    dp.include_router(topics.router)

    print("Бот запущен и готов к работе")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
