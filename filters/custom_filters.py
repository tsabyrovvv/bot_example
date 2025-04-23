import logging
from config import config
from aiogram.types import Message
from typing import Union, Dict, Any
from aiogram.filters import BaseFilter


# Получаем объект логгера с именем 'bot_logger'
# Это хорошая практика - использовать именованные логгеры для удобства настройки уровней логирования
logger = logging.getLogger('bot_logger')


class IsAdmin(BaseFilter):
    """Фильтр для проверки, является ли пользователь администратором"""
    
    async def __call__(self, message: Message) -> bool:
        # Извлекаем ID пользователя из объекта сообщения
        # message.from_user содержит информацию об отправителе сообщения
        user_id = message.from_user.id
        
        # Выводим подробное логирование для отладки
        # Это полезно для поиска проблем при работе с фильтрами
        logger.info(f"IsAdmin фильтр: проверка пользователя {user_id}")
        # Выводим список ID администраторов, полученный из конфигурации
        logger.info(f"Список админов из конфига: {config.bot.admin_ids}")
        
        # Проверяем, входит ли ID пользователя в список администраторов
        # config.bot.admin_ids должен быть списком или множеством с ID администраторов
        is_admin = user_id in config.bot.admin_ids
        # Логируем результат проверки для удобства отладки
        logger.info(f"Результат проверки на админа: {is_admin}")
        
        # Возвращаем результат проверки:
        # True - пользователь является администратором
        # False - пользователь не является администратором
        return is_admin
    