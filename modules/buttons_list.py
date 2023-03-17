from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


class MenuStage(StatesGroup):
    waiting_for_name = State()


# Клавиатура обычная с кнопкой "Меню"
menu_kb = ReplyKeyboardMarkup(resize_keyboard=True) #.add(KeyboardButton('Menu'))
btn_rates = KeyboardButton('⭐️Тарифы')
btn_profile = KeyboardButton('👤 Ваш профиль')
btn_benefit = KeyboardButton('📋 Что вы получаете')
btn_stats = KeyboardButton('📊 Статистика автора')
menu_kb.row(btn_rates, btn_profile)
menu_kb.row(btn_benefit, btn_stats)

# Клавиатура под сообщением с тарифами для доступа
access_kb = InlineKeyboardMarkup().add(InlineKeyboardButton('🔒 Получить доступ', callback_data='access_btn'))

# Сами тарифы
rates_kb = InlineKeyboardMarkup()
three_month = InlineKeyboardButton('🟠 3 месяца', callback_data='three_month')
one_year = InlineKeyboardButton('🟡 1 год', callback_data='one_year')
indefinitely = InlineKeyboardButton('🟢 Бессрочно', callback_data='indefinitely')
rates_kb.row(three_month, one_year, indefinitely)

# Клавиатура для ожидания скрина с платежом
pending_payment_kb = InlineKeyboardMarkup().add(InlineKeyboardButton('✅ Отправить скрин / ссылку на транзакцию', callback_data='pending_payment'))

# Клавиатура для ожидания скрина с платежом
cancel_kb = InlineKeyboardMarkup().add(InlineKeyboardButton('⬅️ Назад', callback_data='cancel_pending_payment'))

