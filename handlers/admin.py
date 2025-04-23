import os
import logging
from aiogram import Dispatcher, types
from aiogram.filters import Command  # Фильтр для обработки команд вида /command
from filters import IsAdmin  # Импорт созданного ранее фильтра для проверки прав администратора
from services.stats_service import get_user_stats, get_message_stats  # Сервисы для получения статистики


# Получаем объект логгера с именем 'bot_logger'
logger = logging.getLogger('bot_logger')


async def cmd_stats(message: types.Message):
    """Обработчик команды /stats для администраторов"""
    # Отправляем сообщение о начале сбора статистики
    await message.answer("Собираю статистику использования бота...")
    
    try:
        # Проверяем наличие psycopg2 - драйвера для работы с PostgreSQL
        try:
            import psycopg2
            db_available = True
        except ImportError:
            # Если драйвер не установлен, сообщаем об этом и прерываем выполнение
            db_available = False
            await message.answer("❌ Драйвер PostgreSQL не установлен. Статистика из БД недоступна.")
            return
            
        # Если драйвер установлен, пробуем получить статистику через сервисные функции
        user_stats = await get_user_stats()  # Статистика по пользователям
        message_stats = await get_message_stats()  # Статистика по сообщениям
        
        # Проверяем, есть ли данные статистики
        if user_stats["total_users"] == 0 and message_stats["total_messages"] == 0:
            # Если статистики нет, показываем информацию о логах как альтернативный источник данных
            # Определяем путь к директории с логами относительно текущего файла
            logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
            # Получаем список файлов в директории с логами (если она существует)
            log_files = os.listdir(logs_dir) if os.path.exists(logs_dir) else []
            
            # Формируем текст сообщения со статистикой (в данном случае - отсутствие статистики)
            stats_text = (
                "📊 <b>Статистика использования бота</b>\n\n"
                "❌ В базе данных нет информации для статистики.\n\n"
                f"📁 <b>Файлы логов</b>: {len(log_files)} файлов\n"
            )
            
            # Добавляем список последних 5 файлов логов (если они есть)
            if log_files:
                stats_text += "\nПоследние 5 файлов логов:\n"
                for log_file in sorted(log_files, reverse=True)[:5]:
                    stats_text += f"• {log_file}\n"
            
            # Отправляем сообщение пользователю
            await message.answer(stats_text)
            return
            
        # Формируем текст с общей статистикой по пользователям и сообщениям
        stats_text = (
            "📊 <b>Статистика использования бота</b>\n\n"
            f"👥 <b>Пользователи:</b>\n"
            f"• Всего уникальных пользователей: {user_stats['total_users']}\n"
            f"• Активных сегодня: {user_stats['active_today']}\n"
            f"• Активных за неделю: {user_stats['active_week']}\n\n"
            f"💬 <b>Сообщения:</b>\n"
            f"• Всего сообщений: {message_stats['total_messages']}\n"
            f"• Сообщений сегодня: {message_stats['today_messages']}\n"
            f"• Сообщений за неделю: {message_stats['week_messages']}\n\n"
        )
        
        # Добавляем топ пользователей, если данные доступны
        if user_stats['top_users']:
            stats_text += "<b>🏆 Топ-5 активных пользователей:</b>\n"
            for i, (username, user_id, count) in enumerate(user_stats['top_users'], 1):
                # Используем username, если он есть, иначе ID пользователя
                display_name = username or f"ID: {user_id}"
                stats_text += f"{i}. {display_name} - {count} сообщений\n"
        
        # Добавляем статистику по дням недели
        days = ["Воскресенье", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
        if message_stats['days_stats']:
            stats_text += "\n<b>📅 Активность по дням недели:</b>\n"
            for day_num, count in message_stats['days_stats']:
                # Преобразуем номер дня недели в название
                day_name = days[int(day_num)]
                stats_text += f"• {day_name}: {count} сообщений\n"
        
        # Отправляем сообщение со статистикой
        await message.answer(stats_text)
        
    except Exception as e:
        # Обработка возможных ошибок
        error_msg = f"Ошибка при получении статистики: {e}"
        # Логируем ошибку
        logger.error(error_msg)
        # Отправляем пользователю сообщение об ошибке
        await message.answer(f"❌ {error_msg}\n\nВозможно, база данных не настроена или недоступна.")


async def cmd_reset_stats(message: types.Message):
    """Обработчик команды /reset_stats для очистки статистики (только для админов)"""
    # В реальном проекте здесь должна быть дополнительная проверка подтверждения
    # Сейчас функция не реализована, отправляем информационное сообщение
    await message.answer("❌ Функция очистки статистики не реализована в текущей версии")


def register_admin_handlers(dp: Dispatcher):
    """Регистрация обработчиков администратора"""
    # Регистрируем обработчик команды /stats с фильтрами Command и IsAdmin
    dp.message.register(cmd_stats, Command("stats"), IsAdmin())
    # Регистрируем обработчик команды /reset_stats с фильтрами Command и IsAdmin
    dp.message.register(cmd_reset_stats, Command("reset_stats"), IsAdmin())
    