from config import config
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties


# Инициализация бота и диспетчера
# Bot - основной класс для взаимодействия с API Telegram
# token - токен бота, полученный от @BotFather
# Устанавливаем HTML как формат разметки для всех сообщений по умолчанию
bot = Bot(token=config.bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


# Диспетчер отвечает за маршрутизацию обновлений от Telegram к соответствующим обработчикам
dp = Dispatcher()
