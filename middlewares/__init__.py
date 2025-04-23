from aiogram import Dispatcher
from .throttling import ThrottlingMiddleware
from .logger import MessageLoggerMiddleware, CallbackLoggerMiddleware


def setup_middlewares(dp: Dispatcher):
    """Настройка middleware"""
    # Ограничение частоты запросов - защита от спама
    # limit=1.0 означает, что обрабатывается не более одного сообщения в секунду от каждого пользователя
    dp.message.middleware(ThrottlingMiddleware(limit=1.0))
    
    # Логирование сообщений и callback-запросов
    # Добавляем middleware для всех входящих текстовых сообщений
    dp.message.middleware(MessageLoggerMiddleware())
    # Добавляем middleware для всех входящих callback запросов (нажатий на инлайн-кнопки)
    dp.callback_query.middleware(CallbackLoggerMiddleware())
    