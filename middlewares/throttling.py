import time
from cachetools import TTLCache
from aiogram.types import Message
from aiogram import BaseMiddleware
from typing import Any, Awaitable, Callable, Dict


class ThrottlingMiddleware(BaseMiddleware):
    """Middleware для ограничения частоты запросов (анти-спам)"""
    
    def __init__(self, limit: float = 0.5):
        """
        Инициализирует middleware с указанным лимитом времени между сообщениями
        
        :param limit: минимальный интервал между сообщениями от одного пользователя (в секундах)
        """
        # Сохраняем лимит времени между сообщениями
        self.limit = limit
        # Кэш для хранения времени последнего сообщения от пользователя
        # TTLCache из библиотеки cachetools автоматически удаляет старые записи
        # maxsize - максимальное количество пользователей в кэше
        # ttl - время жизни записи в секундах (автоматическое удаление)
        self.cache = TTLCache(maxsize=10000, ttl=60)
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        """
        Обработчик сообщений, который проверяет частоту запросов
        и блокирует слишком частые сообщения
        """
        # Получаем ID пользователя из сообщения
        user_id = event.from_user.id
        
        # Получаем текущее время (Unix timestamp)
        current_time = time.time()
        
        # Если пользователь отправляет сообщения слишком часто
        if user_id in self.cache and current_time - self.cache[user_id] < self.limit:
            # Пропускаем обработку сообщения (возвращаем None)
            # Пользователь не получит уведомления о блокировке,
            # сообщение просто не будет обработано
            return None
        
        # Обновляем время последнего сообщения от пользователя
        self.cache[user_id] = current_time
        
        # Продолжаем обработку сообщения
        # Передаем управление следующему middleware или обработчику
        return await handler(event, data)
    