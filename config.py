import os
from dotenv import load_dotenv
from dataclasses import dataclass


# Загружаем переменные окружения из файла .env
# Это позволяет хранить конфиденциальные данные вне кода
load_dotenv()


@dataclass
class BotConfig:
    """
    Конфигурация бота Telegram
    Использование dataclass упрощает создание классов для хранения данных
    """
    token: str                   # Токен бота Telegram
    admin_ids: list[int]         # Список ID администраторов бота
    
    # Параметры подключения к базе данных PostgreSQL
    db_host: str                 # Хост базы данных
    db_port: int                 # Порт базы данных
    db_name: str                 # Имя базы данных
    db_user: str                 # Имя пользователя БД
    db_password: str             # Пароль пользователя БД
    
    # Имена таблиц и колонок в базе данных
    basic_logs_db_table_name: str    # Имя таблицы для основных логов
    errors_logs_db_table_name: str   # Имя таблицы для логов ошибок
    basic_logs_db_column_name: str   # Имя колонки для основных логов
    errors_logs_db_column_name: str  # Имя колонки для логов ошибок
    

@dataclass
class OpenAIConfig:
    """Конфигурация для API OpenAI"""
    api_key: str                 # API ключ OpenAI
    model: str                   # Название модели OpenAI (например, gpt-3.5-turbo)
    

@dataclass
class Config:
    """Общая конфигурация приложения, объединяющая все подконфигурации"""
    bot: BotConfig               # Конфигурация бота
    openai: OpenAIConfig         # Конфигурация OpenAI
    

def load_config() -> Config:
    """
    Загрузка конфигурации из переменных окружения
    
    :return: Объект конфигурации с заполненными значениями
    """
    return Config(
        bot=BotConfig(
            # Получаем токен бота из переменной окружения BOT_TOKEN
            token=os.getenv("BOT_TOKEN"),
            
            # Получаем список ID администраторов, разделенных запятыми,
            # и преобразуем их в целые числа
            admin_ids=[int(admin_id) for admin_id in os.getenv("ADMIN_IDS", "").split(",") if admin_id],
            
            # Настройки подключения к базе данных
            # os.getenv позволяет указать значение по умолчанию,
            # если переменная окружения не задана
            db_host=os.getenv("DB_HOST", "localhost"),
            db_port=int(os.getenv("DB_PORT", "5432")),
            db_name=os.getenv("DB_NAME", "startup_house_bot"),
            db_user=os.getenv("DB_USER", "postgres"),
            db_password=os.getenv("DB_PASSWORD", ""),
            
            # Имена таблиц и колонок
            basic_logs_db_table_name=os.getenv("BASIC_LOGS_DB_TABLE_NAME", "bot_logs"),
            errors_logs_db_table_name=os.getenv("ERRORS_LOGS_DB_TABLE_NAME", "bot_errors"),
            basic_logs_db_column_name=os.getenv("BASIC_LOGS_DB_COLUMN_NAME", "log_entry"),
            errors_logs_db_column_name=os.getenv("ERRORS_LOGS_DB_COLUMN_NAME", "error_entry"),
        ),
        openai=OpenAIConfig(
            # Настройки OpenAI API
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
        )
    )


# Создаем экземпляр конфигурации при импорте модуля
config = load_config()
