import os
import json
import logging
import datetime
from config import config
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Any, Awaitable, Callable, Dict


class LoggerMiddleware(BaseMiddleware):
    """Middleware для логирования всех сообщений в БД и файл"""
    
    def __init__(self):
        """Инициализация middleware логирования"""
        # Настраиваем логирование в файл
        self.setup_file_logging()
        # Получаем экземпляр логгера
        self.logger = logging.getLogger('bot_logger')
        
        # Проверяем возможность подключения к БД
        self.db_available = False
        try:
            # Пытаемся импортировать драйвер PostgreSQL
            import psycopg2
            # Пробуем импортировать, но не подключаемся сразу
            self.db_available = True
            # Сохраняем ссылку на модуль для дальнейшего использования
            self.psycopg2 = psycopg2
        except ImportError:
            # Если импорт не удался, выводим предупреждение
            self.logger.warning("psycopg2 не установлен. Логирование в БД отключено.")
    
    def setup_file_logging(self):
        """Настройка логирования в файл"""
        # Создаем директорию для логов, если не существует
        # Путь относительно текущего файла middleware
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Формируем имя файла с датой для разделения логов по дням
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(logs_dir, f'bot_log_{current_date}.log')
        
        # Настраиваем обработчик файла
        file_handler = logging.FileHandler(log_file)
        # Задаем формат записей лога с временной меткой, уровнем и сообщением
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        # Настраиваем логгер
        logger = logging.getLogger('bot_logger')
        # Устанавливаем уровень логирования INFO и выше (INFO, WARNING, ERROR, CRITICAL)
        logger.setLevel(logging.INFO)
        
        # Избегаем дублирования логов (важно при перезапуске бота)
        if not logger.handlers:
            logger.addHandler(file_handler)
    
    def get_db_connection(self):
        """Получение соединения с базой данных"""
        # Проверяем, доступен ли драйвер БД
        if not self.db_available:
            return None
            
        try:
            # Пытаемся установить соединение с базой данных
            # Все параметры подключения берутся из конфигурации
            conn = self.psycopg2.connect(
                host=config.bot.db_host,
                port=config.bot.db_port,
                database=config.bot.db_name,
                user=config.bot.db_user,
                password=config.bot.db_password
            )
            return conn
        except Exception as e:
            # Логируем ошибку подключения
            self.logger.error(f"Ошибка подключения к БД: {e}")
            return None
    
    def log_to_database(self, event_type: str, user_id: int, username: str, 
                        chat_id: int, text: str, data: Dict[str, Any]):
        """Логирование в базу данных"""
        # Проверяем, доступен ли драйвер БД
        if not self.db_available:
            return
            
        # Получаем соединение с БД
        conn = self.get_db_connection()
        if not conn:
            return
        
        try:
            # Создаем курсор для выполнения SQL-запросов
            with conn.cursor() as cursor:
                # Создаем таблицу, если не существует
                # Используем имя таблицы из конфигурации
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {config.bot.basic_logs_db_table_name} (
                        id SERIAL PRIMARY KEY,                    -- Уникальный идентификатор записи
                        timestamp TIMESTAMP NOT NULL DEFAULT NOW(), -- Время события
                        event_type VARCHAR(50) NOT NULL,          -- Тип события (message/callback)
                        user_id BIGINT NOT NULL,                  -- ID пользователя
                        username VARCHAR(255),                    -- Имя пользователя (может быть NULL)
                        chat_id BIGINT NOT NULL,                  -- ID чата
                        text TEXT,                                -- Текст сообщения/callback
                        data JSONB                                -- Дополнительные данные в JSON
                    )
                """)
                
                # Вставляем запись о событии в таблицу
                cursor.execute(f"""
                    INSERT INTO {config.bot.basic_logs_db_table_name} 
                    (event_type, user_id, username, chat_id, text, data)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (event_type, user_id, username, chat_id, text, json.dumps(data)))
                
                # Фиксируем транзакцию
                conn.commit()
        except Exception as e:
            # Логируем ошибку записи в БД
            self.logger.error(f"Ошибка записи в БД: {e}")
        finally:
            # Закрываем соединение в любом случае
            conn.close()


class MessageLoggerMiddleware(LoggerMiddleware):
    """Middleware для логирования сообщений"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        """Обработчик сообщений для логирования"""
        
        try:
            # Извлекаем данные из объекта сообщения
            user_id = event.from_user.id  # ID пользователя
            username = event.from_user.username  # Имя пользователя (может быть None)
            chat_id = event.chat.id  # ID чата
            text = event.text or "[НЕТ ТЕКСТА]"  # Текст сообщения или заглушка
            event_data = {"message_id": event.message_id}  # Дополнительные данные
            
            # Логируем в файл
            self.logger.info(f"Сообщение от {username or user_id} (ID: {user_id}): {text}")
            
            # Логируем в базу данных (если доступно)
            self.log_to_database(
                event_type="message",  # Тип события
                user_id=user_id,
                username=username,
                chat_id=chat_id,
                text=text,
                data=event_data
            )
        except Exception as e:
            # Логируем ошибку, но не прерываем обработку сообщения
            self.logger.error(f"Ошибка при логировании сообщения: {e}")
        
        # Продолжаем обработку события в любом случае
        # Передаем управление следующему middleware или обработчику
        return await handler(event, data)


class CallbackLoggerMiddleware(LoggerMiddleware):
    """Middleware для логирования callback-запросов (нажатий на инлайн-кнопки)"""
    
    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """Обработчик callback-запросов для логирования"""
        
        try:
            # Извлекаем данные из объекта callback-запроса
            user_id = event.from_user.id  # ID пользователя
            username = event.from_user.username  # Имя пользователя
            # Chat ID может быть недоступен, если запрос пришел из inline режима
            chat_id = event.message.chat.id if event.message else 0
            text = event.data  # Данные callback (обычно строка)
            event_data = {"query_id": event.id}  # Дополнительные данные
            
            # Логируем в файл
            self.logger.info(f"Callback от {username or user_id} (ID: {user_id}): {text}")
            
            # Логируем в базу данных (если доступно)
            self.log_to_database(
                event_type="callback_query",  # Тип события
                user_id=user_id,
                username=username,
                chat_id=chat_id,
                text=text,
                data=event_data
            )
        except Exception as e:
            # Логируем ошибку, но не прерываем обработку callback
            self.logger.error(f"Ошибка при логировании callback: {e}")
        
        # Продолжаем обработку события в любом случае
        # Передаем управление следующему middleware или обработчику
        return await handler(event, data)
    