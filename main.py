import asyncio
import logging
from bot import bot, dp
from middlewares import setup_middlewares
from handlers import register_all_handlers


# Настройка логирования
# Устанавливаем базовую конфигурацию для стандартной библиотеки logging
logging.basicConfig(
    level=logging.INFO,                  # Уровень логирования (INFO и выше)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"  # Формат сообщений лога
)


async def main():
    """
    Основная асинхронная функция, инициализирующая и запускающая бота
    """
    # Установка middleware
    # Middleware обрабатывают сообщения до и после обработчиков
    setup_middlewares(dp)
    
    # Регистрация всех обработчиков сообщений и команд
    register_all_handlers(dp)
    
    # Запуск бота в режиме long polling (постоянный опрос серверов Telegram)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        # Запускаем асинхронную функцию main() в цикле событий asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        # Корректное завершение при нажатии Ctrl+C
        logging.info("Бот остановлен!")
