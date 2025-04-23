from aiogram.filters import Command  # Фильтр для обработки команд
from keyboards.reply import get_main_keyboard # Импортируем клавиатуру
from aiogram import Dispatcher, F, types  # F используется для создания составных фильтров


async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    # Отправляем приветственное сообщение при запуске бота
    await message.answer(
        "Привет! 👋 Добро пожаловать в Startup House! 🚀\n\n"
        "Я бот-помощник, который может ответить на вопросы о стартапах, бизнесе и ИИ.\n\n"
        "Что вас интересует сегодня?",
        reply_markup=get_main_keyboard()  # Добавляем клавиатуру
    )


async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    # Отправляем справочную информацию о возможностях бота
    await message.answer(
        "Я могу ответить на ваши вопросы о стартапах, бизнесе и ИИ.\n\n"
        "Просто напишите сообщение, содержащее интересующую вас тему!"
    )


def register_common_handlers(dp: Dispatcher):
    """Регистрация общих обработчиков"""
    # Регистрируем обработчик команды /start
    dp.message.register(cmd_start, Command("start"))
    # Регистрируем обработчик команды /help
    dp.message.register(cmd_help, Command("help"))
