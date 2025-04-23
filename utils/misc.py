import logging
from typing import List, Set, Dict, Any


def extract_keywords(text: str) -> Set[str]:
    """
    Извлекает ключевые слова из текста
    
    :param text: Входной текст
    :return: Множество ключевых слов
    """
    # Приводим текст к нижнему регистру для унификации
    # Это позволяет обрабатывать слова независимо от регистра
    text_lower = text.lower()
    
    # Разделяем на слова по пробелам
    words = text_lower.split()
    
    # Удаляем знаки препинания и приводим к общему виду
    # strip() удаляет указанные символы с начала и конца строки
    clean_words = [word.strip('.,!?:;()[]{}"\'-') for word in words]
    
    # Фильтруем короткие слова (длиной менее 3 символов) и возвращаем уникальные слова
    # set() преобразует список в множество, убирая дубликаты
    return set(word for word in clean_words if len(word) > 2)


def log_user_message(user_id: int, username: str, message: str) -> None:
    """
    Логирует сообщение пользователя
    
    :param user_id: ID пользователя
    :param username: Имя пользователя
    :param message: Текст сообщения
    """
    # Записывает информацию о сообщении пользователя в лог 
    # с уровнем INFO, включая ID пользователя, имя и текст сообщения
    logging.info(f"Сообщение от пользователя {user_id} (@{username}): {message}")
