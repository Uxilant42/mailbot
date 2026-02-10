
from aiogram import Bot, Dispatcher
import asyncio
from config import BOT_TOKEN
from handlers import router

# ============================================
# ИНИЦИАЛИЗАЦИЯ
# ============================================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ============================================
# РЕГИСТРАЦИЯ ХЕНДЛЕРОВ
# ============================================
dp.include_router(router)

# ============================================
# ФУНКЦИЯ ЗАПУСКА
# ============================================
async def main():
    """Запускает бота в режиме long polling"""
    print("Бот запущен!")
    await dp.start_polling(bot)

# ============================================
# ТОЧКА ВХОДА
# ============================================
if __name__ == '__main__':
    asyncio.run(main())
