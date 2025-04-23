from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_topics_keyboard() -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру с темами для обсуждения
    
    :return: Объект InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Бизнес-план", callback_data="topic:business_plan"),
                InlineKeyboardButton(text="Привлечение инвестиций", callback_data="topic:investments")
            ],
            [
                InlineKeyboardButton(text="Маркетинг", callback_data="topic:marketing"),
                InlineKeyboardButton(text="Команда", callback_data="topic:team")
            ],
            [
                InlineKeyboardButton(text="ИИ в бизнесе", callback_data="topic:ai_business")
            ]
        ]
    )
    return keyboard
