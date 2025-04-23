import openai
import logging
from config import config


# Настройка клиента OpenAI
# Инициализируем клиент для работы с OpenAI API, передавая API ключ из конфигурации
client = openai.OpenAI(api_key=config.openai.api_key)


async def generate_response(prompt: str) -> str:
    """
    Генерирует ответ с использованием OpenAI API
    
    :param prompt: Текст запроса пользователя
    :return: Ответ от API
    """
    try:
        # Если API ключ не настроен, используем заглушку
        # Это позволяет боту работать даже без ключа API
        if not config.openai.api_key:
            return generate_fallback_response(prompt)
            
        # Формируем системную инструкцию
        # Это определяет поведение модели, её тон и стиль
        system_message = """
        Ты - помощник бота Startup House. Твоя задача - помогать пользователям 
        с вопросами о стартапах, бизнесе и искусственном интеллекте.
        Отвечай кратко, дружелюбно и информативно. Используй эмодзи.
        """
        
        # Отправляем запрос к API
        # Создаем запрос на генерацию ответа используя chat.completions.create
        response = client.chat.completions.create(
            model=config.openai.model,  # Используем модель из конфигурации
            messages=[
                {"role": "system", "content": system_message},  # Системное сообщение
                {"role": "user", "content": prompt}  # Сообщение пользователя
            ],
            max_tokens=500,  # Ограничиваем длину ответа
            temperature=0.7  # Настраиваем креативность (0.7 - умеренная)
        )
        
        # Получаем ответ
        # Извлекаем содержимое первого сообщения из ответа
        return response.choices[0].message.content
        
    except Exception as e:
        # Обрабатываем любые возможные ошибки
        logging.error(f"Ошибка при запросе к OpenAI API: {e}")
        # В случае ошибки возвращаем ответ из заглушки
        return generate_fallback_response(prompt)


def generate_fallback_response(prompt: str) -> str:
    """
    Генерирует ответ без использования API (заглушка)
    Используется когда API недоступен или произошла ошибка
    
    :param prompt: Текст запроса пользователя
    :return: Ответ-заглушка
    """
    # Простая логика для ответов без API
    # Проверяем наличие ключевых слов в запросе пользователя
    prompt_lower = prompt.lower()
    
    # Серия условий для определения темы и возврата соответствующего ответа
    if "бизнес-план" in prompt_lower:
        return "Для создания хорошего бизнес-плана важно учесть анализ рынка, финансовый план и стратегию маркетинга. 📊"
    elif "инвестиции" in prompt_lower or "инвестор" in prompt_lower:
        return "Привлечение инвестиций - важный этап развития стартапа. Рекомендую подготовить питч-деку и прототип продукта. 💰"
    elif "маркетинг" in prompt_lower:
        return "Для эффективного маркетинга стартапа важно определить целевую аудиторию и каналы привлечения клиентов. 🎯"
    elif "команда" in prompt_lower:
        return "Сильная команда - один из ключевых факторов успеха стартапа. Ищите людей, дополняющих ваши навыки. 👥"
    else:
        # Если не удалось определить тему, возвращаем универсальный ответ
        return "Интересный вопрос! Я записал его и передам команде Startup House для подготовки развернутого ответа. 📝"
    