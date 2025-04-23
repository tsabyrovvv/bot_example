from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает основную клавиатуру с кнопками
    
    :return: Объект ReplyKeyboardMarkup
    """
    # Создаем обычную клавиатуру, которая появляется вместо клавиатуры устройства
    # ReplyKeyboardMarkup используется для создания постоянных кнопок под полем ввода
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            # Первый ряд кнопок с эмодзи для лучшей визуализации
            [
                # При нажатии на кнопку, её текст отправляется как обычное сообщение
                KeyboardButton(text="🚀 О стартапах"),
                KeyboardButton(text="💡 Об ИИ")
            ],
            # Второй ряд кнопок
            [
                KeyboardButton(text="💼 О бизнесе"),
                KeyboardButton(text="❓ Помощь")
            ]
        ],
        # resize_keyboard=True делает кнопки меньше и компактнее
        resize_keyboard=True,
        # input_field_placeholder задает текст-подсказку в поле ввода сообщения
        input_field_placeholder="Выберите тему или задайте вопрос..."
    )
    # Возвращаем созданную клавиатуру
    return keyboard
