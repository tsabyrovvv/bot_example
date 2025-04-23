import os
import sys
import logging
import psycopg2


# Добавляем родительский каталог в sys.path для импорта config
# Это позволяет импортировать модули из родительской директории
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config


def init_database():
    """Инициализация базы данных и создание необходимых таблиц"""
    conn = None
    try:
        # Подключаемся к базе данных PostgreSQL используя параметры из конфигурации
        conn = psycopg2.connect(
            host=config.bot.db_host,      # Хост/IP-адрес сервера БД
            port=config.bot.db_port,      # Порт PostgreSQL
            database=config.bot.db_name,  # Имя базы данных
            user=config.bot.db_user,      # Имя пользователя БД
            password=config.bot.db_password  # Пароль пользователя БД
        )
        
        # Создаем курсор для выполнения SQL-запросов
        with conn.cursor() as cursor:
            # Создаем таблицу для основных логов, если она не существует
            # Эта таблица хранит информацию о сообщениях и взаимодействиях пользователей с ботом
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {config.bot.basic_logs_db_table_name} (
                    id SERIAL PRIMARY KEY,                    -- Уникальный ID записи
                    timestamp TIMESTAMP NOT NULL DEFAULT NOW(), -- Время события
                    event_type VARCHAR(50) NOT NULL,          -- Тип события (message, callback и т.д.)
                    user_id BIGINT NOT NULL,                  -- ID пользователя Telegram
                    username VARCHAR(255),                    -- Имя пользователя Telegram (необязательное)
                    chat_id BIGINT NOT NULL,                  -- ID чата
                    text TEXT,                                -- Текст сообщения/запроса
                    data JSONB                                -- Дополнительные данные в формате JSON
                )
            """)
            
            # Создаем таблицу для логирования ошибок, если она не существует
            # Эта таблица хранит информацию об ошибках и исключениях, возникающих при работе бота
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {config.bot.errors_logs_db_table_name} (
                    id SERIAL PRIMARY KEY,                    -- Уникальный ID записи
                    timestamp TIMESTAMP NOT NULL DEFAULT NOW(), -- Время ошибки
                    level VARCHAR(50) NOT NULL,               -- Уровень ошибки (ERROR, CRITICAL и т.д.)
                    module VARCHAR(255),                      -- Модуль, в котором произошла ошибка
                    function VARCHAR(255),                    -- Функция, в которой произошла ошибка
                    error_message TEXT,                       -- Текст сообщения об ошибке
                    traceback TEXT,                           -- Трассировка стека вызовов
                    user_id BIGINT,                           -- ID пользователя (если ошибка связана с пользователем)
                    extra_data JSONB                          -- Дополнительные данные в формате JSON
                )
            """)
            
            # Создаем индексы для оптимизации запросов
            # Индексы ускоряют выборку данных по часто используемым полям
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_logs_user_id ON {config.bot.basic_logs_db_table_name} (user_id);
                CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON {config.bot.basic_logs_db_table_name} (timestamp);
                CREATE INDEX IF NOT EXISTS idx_logs_event_type ON {config.bot.basic_logs_db_table_name} (event_type);
                
                CREATE INDEX IF NOT EXISTS idx_errors_timestamp ON {config.bot.errors_logs_db_table_name} (timestamp);
                CREATE INDEX IF NOT EXISTS idx_errors_level ON {config.bot.errors_logs_db_table_name} (level);
                CREATE INDEX IF NOT EXISTS idx_errors_user_id ON {config.bot.errors_logs_db_table_name} (user_id);
            """)
            
            # Подтверждаем изменения в базе данных
            conn.commit()
            
            print("База данных успешно инициализирована!")
            
    except Exception as e:
        # Обрабатываем возможные ошибки при подключении или выполнении запросов
        print(f"Ошибка при инициализации базы данных: {e}")
        # Откатываем изменения, если произошла ошибка
        if conn:
            conn.rollback()
    finally:
        # Закрываем соединение с базой данных в любом случае
        if conn:
            conn.close()


# Проверяем, запущен ли скрипт напрямую (а не импортирован)
if __name__ == "__main__":
    # Если скрипт запущен напрямую, инициализируем базу данных
    init_database()
