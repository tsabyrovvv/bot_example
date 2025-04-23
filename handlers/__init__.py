from aiogram import Dispatcher
from .user import register_user_handlers
from .admin import register_admin_handlers
from .common import register_common_handlers


def register_all_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков"""
    # Создаем кортеж из функций-регистраторов обработчиков
    # Порядок важен! Обработчики будут регистрироваться в указанном порядке
    # Обычно сначала регистрируются общие, затем специфичные обработчики
    handlers = (
        register_common_handlers,  # Общие обработчики (старт, помощь и т.д.)
        register_admin_handlers,   # Обработчики для администраторов
        register_user_handlers,    # Обработчики для обычных пользователей
    )
    
    # Проходим по всем функциям-регистраторам и вызываем их,
    # передавая в качестве аргумента объект диспетчера
    for handler in handlers:
        handler(dp)
        