from aiogram import Dispatcher, F, types
from keyboards.inline import get_topics_keyboard # Импортируем клавиатуру
from services.openai_service import generate_response  # Сервис для генерации ответов с помощью OpenAI


# Обработчик приветствий
async def handle_greeting(message: types.Message):
    """Обработчик приветствий"""
    # Отвечаем на приветствие пользователя
    await message.answer("Привет! Добро пожаловать в Startup House! 🚀")


# Обработчик ключевых слов, связанных с ИИ
async def handle_ai_keywords(message: types.Message):
    """Обработчик ключевых слов, связанных с ИИ"""
    # Отвечаем на сообщения, содержащие ключевые слова по теме ИИ
    await message.answer("Интересная тема! Расскажи, как ты используешь ИИ в бизнесе? 💡")


# Обработчик ключевых слов, связанных с бизнесом
async def handle_business_keywords(message: types.Message):
    """Обработчик ключевых слов, связанных с бизнесом"""
    # Отвечаем на сообщения, содержащие ключевые слова по теме бизнеса
    await message.answer("Бизнес и стартапы - захватывающая тема! Что конкретно тебя интересует? 💼",
                         reply_markup=get_topics_keyboard())


# Обработчик для прочих сообщений (будет использовать OpenAI API)
async def handle_other_messages(message: types.Message):
    """Обработчик для прочих сообщений"""
    # Генерируем ответ с помощью OpenAI API для всех остальных сообщений
    response = await generate_response(message.text)
    # Отправляем сгенерированный ответ пользователю
    await message.answer(response)


def register_user_handlers(dp: Dispatcher):
    """Регистрация обработчиков пользователя"""
    # Приветствия - используем F.text.contains вместо Text для проверки наличия ключевых слов
    # | - оператор логического "ИЛИ" для объединения фильтров
    dp.message.register(
        handle_greeting, 
        F.text.lower().contains("привет") | 
        F.text.lower().contains("здравствуй") | 
        F.text.lower().contains("хай") | 
        F.text.lower().contains("hello") | 
        F.text.lower().contains("hi")
    )
    
    # Ключевые слова, связанные с ИИ - регистрируем обработчик для сообщений, 
    # содержащих слова из области искусственного интеллекта
    dp.message.register(
        handle_ai_keywords,
        F.text.lower().contains("ии") | 
        F.text.lower().contains("искусственный интеллект") | 
        F.text.lower().contains("ai") | 
        F.text.lower().contains("нейросеть") | 
        F.text.lower().contains("нейронка") | 
        F.text.lower().contains("chatgpt") | 
        F.text.lower().contains("gpt")
    )
    
    # Ключевые слова, связанные с бизнесом - регистрируем обработчик для сообщений,
    # содержащих слова из области бизнеса и предпринимательства
    dp.message.register(
        handle_business_keywords,
        F.text.lower().contains("бизнес") | 
        F.text.lower().contains("стартап") | 
        F.text.lower().contains("предпринимательство") | 
        F.text.lower().contains("startup") | 
        F.text.lower().contains("business")
    )
    
    # Прочие сообщения - этот обработчик сработает для всех остальных сообщений,
    # не попавших под предыдущие фильтры
    dp.message.register(handle_other_messages)
