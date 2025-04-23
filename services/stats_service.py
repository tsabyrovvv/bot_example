import logging
import psycopg2
import datetime
from config import config


# Получаем экземпляр логгера
logger = logging.getLogger('bot_logger')


async def get_user_stats():
    """
    Получение статистики по пользователям из базы данных
    
    :return: Словарь со статистикой
    """
    conn = None
    try:
        # Устанавливаем соединение с базой данных PostgreSQL
        conn = psycopg2.connect(
            host=config.bot.db_host,
            port=config.bot.db_port,
            database=config.bot.db_name,
            user=config.bot.db_user,
            password=config.bot.db_password
        )
        
        with conn.cursor() as cursor:
            # Проверяем существование таблицы в базе данных
            # Это предотвращает ошибки, если таблица ещё не создана
            cursor.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = '{config.bot.basic_logs_db_table_name}'
                )
            """)
            table_exists = cursor.fetchone()[0]
            
            # Если таблица не существует, возвращаем пустую статистику
            if not table_exists:
                return {
                    "total_users": 0,
                    "active_today": 0,
                    "active_week": 0,
                    "top_users": []
                }
                
            # Общее количество уникальных пользователей
            # COUNT(DISTINCT user_id) считает только уникальные user_id
            cursor.execute(f"""
                SELECT COUNT(DISTINCT user_id) 
                FROM {config.bot.basic_logs_db_table_name}
            """)
            total_users = cursor.fetchone()[0]
            
            # Количество активных пользователей за сегодня
            # Фильтруем по дате текущего дня
            today = datetime.datetime.now().date()
            cursor.execute(f"""
                SELECT COUNT(DISTINCT user_id) 
                FROM {config.bot.basic_logs_db_table_name}
                WHERE DATE(timestamp) = %s
            """, (today,))
            active_today = cursor.fetchone()[0]
            
            # Количество активных пользователей за неделю
            # Фильтруем по дате начиная с 7 дней назад
            week_ago = today - datetime.timedelta(days=7)
            cursor.execute(f"""
                SELECT COUNT(DISTINCT user_id) 
                FROM {config.bot.basic_logs_db_table_name}
                WHERE DATE(timestamp) >= %s
            """, (week_ago,))
            active_week = cursor.fetchone()[0]
            
            # Топ-5 активных пользователей
            # Группируем по пользователям и сортируем по количеству сообщений
            cursor.execute(f"""
                SELECT username, user_id, COUNT(*) as msg_count
                FROM {config.bot.basic_logs_db_table_name}
                GROUP BY username, user_id
                ORDER BY msg_count DESC
                LIMIT 5
            """)
            top_users = cursor.fetchall()
            
            # Возвращаем словарь со всей собранной статистикой
            return {
                "total_users": total_users,
                "active_today": active_today,
                "active_week": active_week,
                "top_users": top_users
            }
    
    except Exception as e:
        # Обрабатываем любые возможные ошибки и логируем их
        logger.error(f"Ошибка получения статистики пользователей: {e}")
        # В случае ошибки возвращаем пустую статистику
        return {
            "total_users": 0,
            "active_today": 0,
            "active_week": 0,
            "top_users": []
        }
    
    finally:
        # Закрываем соединение с БД в любом случае, если оно было установлено
        if conn:
            conn.close()


async def get_message_stats():
    """
    Получение статистики по сообщениям из базы данных
    
    :return: Словарь со статистикой
    """
    conn = None
    try:
        # Устанавливаем соединение с базой данных
        conn = psycopg2.connect(
            host=config.bot.db_host,
            port=config.bot.db_port,
            database=config.bot.db_name,
            user=config.bot.db_user,
            password=config.bot.db_password
        )
        
        with conn.cursor() as cursor:
            # Проверяем существование таблицы
            cursor.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = '{config.bot.basic_logs_db_table_name}'
                )
            """)
            table_exists = cursor.fetchone()[0]
            
            # Если таблица не существует, возвращаем пустую статистику
            if not table_exists:
                return {
                    "total_messages": 0,
                    "today_messages": 0,
                    "week_messages": 0,
                    "days_stats": []
                }
                
            # Общее количество сообщений
            # Фильтруем только по типу события 'message'
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM {config.bot.basic_logs_db_table_name}
                WHERE event_type = 'message'
            """)
            total_messages = cursor.fetchone()[0]
            
            # Количество сообщений за сегодня
            today = datetime.datetime.now().date()
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM {config.bot.basic_logs_db_table_name}
                WHERE event_type = 'message' AND DATE(timestamp) = %s
            """, (today,))
            today_messages = cursor.fetchone()[0]
            
            # Количество сообщений за неделю
            week_ago = today - datetime.timedelta(days=7)
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM {config.bot.basic_logs_db_table_name}
                WHERE event_type = 'message' AND DATE(timestamp) >= %s
            """, (week_ago,))
            week_messages = cursor.fetchone()[0]
            
            # Статистика по дням недели
            # EXTRACT(DOW FROM timestamp) извлекает день недели (0-6, где 0 = воскресенье)
            cursor.execute(f"""
                SELECT EXTRACT(DOW FROM timestamp) as day_of_week, COUNT(*) as count
                FROM {config.bot.basic_logs_db_table_name}
                WHERE event_type = 'message' AND timestamp >= %s
                GROUP BY day_of_week
                ORDER BY day_of_week
            """, (week_ago,))
            days_stats = cursor.fetchall()
            
            # Возвращаем словарь со всей собранной статистикой
            return {
                "total_messages": total_messages,
                "today_messages": today_messages,
                "week_messages": week_messages,
                "days_stats": days_stats
            }
    
    except Exception as e:
        # Обрабатываем любые возможные ошибки и логируем их
        logger.error(f"Ошибка получения статистики сообщений: {e}")
        # В случае ошибки возвращаем пустую статистику
        return {
            "total_messages": 0,
            "today_messages": 0,
            "week_messages": 0,
            "days_stats": []
        }
    
    finally:
        # Закрываем соединение с БД в любом случае, если оно было установлено
        if conn:
            conn.close()
