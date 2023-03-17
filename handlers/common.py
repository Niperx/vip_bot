import logging
import sqlite3
import calendar
import locale
import config
from datetime import datetime, date
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from modules.buttons_list import menu_kb, access_kb, rates_kb, pending_payment_kb, cancel_kb
from modules.admins_list import ADMINS

bot = Bot(token=config.TOKEN)
admin = ADMINS[0]
locale.setlocale(locale.LC_ALL, "ru")


class PaymentStage(StatesGroup):
    waiting_for_pending = State()


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def create_user(user_id, link):  # создание нового солдата для профиля
    user_info = (user_id, False, None, link, datetime.now())
    conn = sqlite3.connect('db/main.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO users VALUES(?,?,?,?,?);", user_info)
    conn.commit()


def check_count(user_id):  # кол-во солдат на текущем пользователе
    conn = sqlite3.connect('db/main.db')
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE user_id = ?", (user_id,))
    count = cur.fetchall()[0][0]
    return count


def load_user(user_id):  # загрузка всей инфы о солдате
    conn = sqlite3.connect('db/main.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    result = cur.fetchone()
    return result


def edit_user(user_id, hm):  # sub_time - время реги + месяцы, hm - проверить сколько добавить месяцев
    conn = sqlite3.connect('db/main.db')
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET subscribed = ?, sub_time = ? WHERE user_id = ? ",
        (1, add_months(datetime.now(), hm), user_id))  # datetime.now() + sub_time
    conn.commit()


def delete_sub(user_id):
    conn = sqlite3.connect('db/main.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET subscribed = ?, sub_time = ? WHERE user_id = ?", (0, None, user_id,))
    conn.commit()


def get_user_stats():
    conn = sqlite3.connect('db/main.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    result = cur.fetchall()
    return result


def get_info_about_user_message(message):
    text = f'\n##### {datetime.now()} #####\n'
    text += f'ID: {message.from_user.id}, Text: {message.text}'
    try:
        text += f'\nUsername: {message.from_user.username},' \
                f' Name: {message.from_user.first_name},' \
                f' Surname: {message.from_user.last_name} '
    except Exception as e:
        logging.exception(e)
        text += 'Нет имени'
    return text


def get_info_about_user_callback(callback):
    text = f'\n##### {datetime.now()} #####\n'
    text += f'ID: {callback.from_user.id}, Text: {callback.data}'
    try:
        text += f'\nUsername: {callback.from_user.username},' \
                f' Name: {callback.from_user.first_name},' \
                f' Surname: {callback.from_user.last_name} '
    except Exception as e:
        logging.exception(e)
        text += 'Нет имени'
    return text


async def cmd_start(message: types.Message):
    print(get_info_about_user_message(message))
    await message.answer("Здравствуйте, это бот для вступления в приватный канал + чат Криптолога",
                         reply_markup=menu_kb)
    cnt = check_count(message.from_user.id)
    if not cnt:
        try:
            create_user(message.from_user.id, f'https://t.me/{message.from_user.username}')
        except:
            create_user(message.from_user.id, f'{message.from_user.first_name} {message.from_user.last_name}')


async def cmd_access(message: types.Message):
    print(get_info_about_user_message(message))
    await message.answer("Условия вступления в наши вип ресурсы (чат/канал/марафон канал/обучающие видео и т.д.)\n"
                         "🟠 3 месяца (пробный) : 340$\n"
                         "🟡 1 год : 580$\n"
                         "🟢 Бессрочно : 850$",
                         reply_markup=access_kb, parse_mode='Markdown')


# прогрузка профиля
async def cmd_profile(message: types.Message):
    print(get_info_about_user_message(message))
    user_info = load_user(message.from_user.id)
    print(user_info)
    subs = '💳 Нет подписок'
    subs_text = 'отсутствует'
    sub_content = ''
    if user_info[1]:
        subs_end = datetime.strptime(user_info[2], '%Y-%m-%d')
        subs_text = subs_end.strftime('%a, %d %b %Y')  # вт, 9 мая 2023г
        days = subs_end - datetime.now()
        subs = f'💳 Подписка на закрытые каналы - {days.days} дн.'
        sub_content = 'Доступы :\n' \
                      'Чат - https://t.me/+KbKbcD_w6A0wYTQy\n' \
                      'Канал - https://t.me/+pX5c6_9xsvM3MjBi\n' \
                      'Cетки байбит - https://t.me/+5ZCXziyOJcQzY2Vi\n' \
                      'Марафон - https://t.me/+MiRU14aTKO9iODky'
    await message.answer(
        f"id: [{message.from_user.id}](tg://user?id{message.from_user.id}) - 👤 [{message.from_user.first_name}](tg://user?id{message.from_user.id})\n\n"
        f"*Активные подписки:*\n"
        f"{subs}\n"
        f"До: {subs_text.lower()}\n\n"
        f"{sub_content}",
        parse_mode='Markdown')


async def cmd_benefit(message: types.Message):
    print(get_info_about_user_message(message))
    await message.answer(
        f"▪️ Вип чат , без флуда, только по крипте, есть много очень толковых ребят которые и вам могут помочь, у которых можно чему-то научится, в чате вы получите нативное обучение нашим стратегиям торговле сеточной торговлей.\n"
        f"▪️ Вип канал с основными сигналами, которые я торгую со своего основного аккаунта + иногда различная важная информация.\n"
        f"▪️ Канал с марафоном, шоу для ютуб в котором мы торгуем суммой в 2000 USDT и смотрим сколько сделаем профита за месяц, планирую проводить его каждый месяц, в канале даю сигналы о входах и выходах из сделок.\n"
        f"▪️ Видео курс обучение от меня,  45 минут сжатой, важной базовой информации для новичков\n"
        f"▪️ Канал со спотовой моей торговлей на Bybit, сеточная торговля, но спотовая \n"
        f"▪️ Сбор пуллов в проекты, в проекты где важен большой вклад для бОльших заработков / различные пуллы STEPN (для заработка команды)\n"
        f"▪️ Ну и моя личка открыта для вас почти круглосуточно для любых вопросов , любой помощи по крипте.\n",
        parse_mode='Markdown')


async def cmd_stats(message: types.Message):
    print(get_info_about_user_message(message))
    await message.answer(f"При нажатии на нее вылезет видео + пару скринов которые я дам тебе скоро ",
                         parse_mode='Markdown')


async def cmd_check_subs(message: types.Message):
    print(get_info_about_user_message(message))
    users_data = get_user_stats()
    subs = []
    for user in users_data:
        if user[1] != 0:
            subs.append(user)
    print(subs)
    text = 'Нет близжайших отписок'
    if subs:
        subs_end = []
        for sub in subs:
            sub_end = datetime.strptime(sub[2], '%Y-%m-%d')
            days = sub_end - datetime.now()
            if days.days < 10:
                subs_end.append(sub)

        if subs_end:
            text = ''
        for user in subs_end:
            status = "Активна" if user[1] != 0 else "Не активна"
            user_end = datetime.strptime(user[2], '%Y-%m-%d') - datetime.now()
            text += f'*ID*: `{user[0]}`\n' \
                    f'*Profile link:* {user[3]}\n' \
                    f'*Статус подписки:* {status}\n' \
                    f'*До конца подписки:* {user_end.days} дн.\n\n'
    await message.reply(text, parse_mode='Markdown')


async def cmd_delete_subs(message: types.Message):
    print(get_info_about_user_message(message))
    print(message.get_args())
    delete_sub(message.get_args())
    await message.reply('Подписка отменена')


# callbacks
async def process_benefit(callback_query: types.CallbackQuery):
    print(get_info_about_user_callback(callback_query))
    await callback_query.message.edit_text(f"🤘 Выберите необходимый вам тариф:",
                                           reply_markup=rates_kb,
                                           parse_mode='Markdown')


# виды платежей
async def process_three_month(callback_query: types.CallbackQuery, state: FSMContext):
    print(get_info_about_user_callback(callback_query))
    await state.update_data(plan='3 месяца')
    await callback_query.message.edit_text(
        f"Оплатите 340 usdt на любой из кошельков и прикрепите скриншот, либо ссылку на транзакцию.\n\n"
        f"ERC20 USDT : \n`0xBF10ecA7492bB0aB812A1635C8779E3E2A0E2147`\n"
        f"BEP20 USDT : \n`0xBF10ecA7492bB0aB812A1635C8779E3E2A0E2147`\n"
        f"BEP20 BUSD : \n`0xBF10ecA7492bB0aB812A1635C8779E3E2A0E2147`\n"
        f"TRC20 USDT : \n`TTg3Sv8dpgjhBeAixA4t2RgSBrqaJ3dmJw`",
        reply_markup=pending_payment_kb,
        parse_mode='Markdown')


async def process_one_year(callback_query: types.CallbackQuery, state: FSMContext):
    print(get_info_about_user_callback(callback_query))
    await state.update_data(plan='1 год')
    await callback_query.message.edit_text(
        f"Оплатите 580 usdt на любой из кошельков и прикрепите скриншот, либо ссылку на транзакцию.\n\n"
        f"ERC20 USDT : \n`0xBF10ecA7492bB0aB812A1635C8779E3E2A0E2147`\n"
        f"BEP20 USDT : \n`0xBF10ecA7492bB0aB812A1635C8779E3E2A0E2147`\n"
        f"BEP20 BUSD : \n`0xBF10ecA7492bB0aB812A1635C8779E3E2A0E2147`\n"
        f"TRC20 USDT : \n`TTg3Sv8dpgjhBeAixA4t2RgSBrqaJ3dmJw`",
        reply_markup=pending_payment_kb,
        parse_mode='Markdown')


async def process_indefinitely(callback_query: types.CallbackQuery, state: FSMContext):
    print(get_info_about_user_callback(callback_query))
    await state.update_data(plan='бессрочно')
    await callback_query.message.edit_text(
        f"Оплатите 850 usdt на любой из кошельков и прикрепите скриншот, либо ссылку на транзакцию.\n\n"
        f"ERC20 USDT : \n`0xBF10ecA7492bB0aB812A1635C8779E3E2A0E2147`\n"
        f"BEP20 USDT : \n`0xBF10ecA7492bB0aB812A1635C8779E3E2A0E2147`\n"
        f"BEP20 BUSD : \n`0xBF10ecA7492bB0aB812A1635C8779E3E2A0E2147`\n"
        f"TRC20 USDT : \n`TTg3Sv8dpgjhBeAixA4t2RgSBrqaJ3dmJw`",
        reply_markup=pending_payment_kb,
        parse_mode='Markdown')


async def process_pending_payment(callback_query: types.CallbackQuery):
    print(get_info_about_user_callback(callback_query))
    await callback_query.message.edit_text(f"Ожидание платежа...\n\n"
                                           f"❗️ ПРИКРЕПИТЕ ФОТО ЧЕКА ЛИБО ССЫЛКУ ❗️\n\n"
                                           f'Нажмите на кнопку "⬅️ Назад", если что-то пошло не так или вы передумали',
                                           reply_markup=cancel_kb,
                                           parse_mode='Markdown')
    await PaymentStage.waiting_for_pending.set()


# получаем фотку
async def cmd_get_photo(message: types.Message, state: FSMContext):
    print(get_info_about_user_message(message))
    user_data = await state.get_data()
    await message.answer('Спасибо за информацию, подтверждаем транзакцию от администратора, ожидайте...')
    await bot.send_message(admin,
                           f"Попытка оплаты подписки на *{user_data['plan'].upper()}*\n\n"
                           f'Возможности:\n"+3" _- 3 месяца_, "+12" _- 1 год_, "+00" _- бессрочно_\n\n'
                           f'Сообщение от пользователя [{message.from_user.id}](tg://user?id{message.from_user.id}) - 👤 [{message.from_user.first_name}](https://t.me/{message.from_user.username}):',
                           parse_mode='Markdown')

    await bot.forward_message(admin, from_chat_id=message.chat.id, message_id=message.message_id)

    await state.finish()


async def cmd_get_confirmation(message: types.Message):
    print(get_info_about_user_message(message))
    confirmation = message.text
    print(message)
    print(confirmation)
    if confirmation[0] == '+':
        chat_pasta = 'Доступы :\n\n' \
                     'Чат - https://t.me/+KbKbcD_w6A0wYTQy\n' \
                     'Канал - https://t.me/+pX5c6_9xsvM3MjBi\n' \
                     'Cетки байбит - https://t.me/+5ZCXziyOJcQzY2Vi\n' \
                     'Марафон - https://t.me/+MiRU14aTKO9iODky'
        if confirmation[1:] == '3':
            print('YES3')
            edit_user(message.reply_to_message.forward_from.id, 3)
            await bot.send_message(message.reply_to_message.forward_from.id,
                                   '👌 Платеж подтвержден. Вы приобрели подписку на 3 месяца.\n' + chat_pasta,
                                   reply_markup=menu_kb)
            await message.answer('Одобрено на 3 месяца')
        elif confirmation[1:] == '12':
            print('YES12')
            edit_user(message.reply_to_message.forward_from.id, 12)
            await bot.send_message(message.reply_to_message.forward_from.id,
                                   '👌 Платеж подтвержден. Вы приобрели подписку на 12 месяцев.\n' + chat_pasta,
                                   reply_markup=menu_kb)
            await message.answer('Одобрено на 12 месяцев')
        elif confirmation[1:] == '00':
            print('YES00')
            edit_user(message.reply_to_message.forward_from.id, 300)
            await bot.send_message(message.reply_to_message.forward_from.id,
                                   '👌 Платеж подтвержден. Вы приобрели подписку навсегда.\n' + chat_pasta,
                                   reply_markup=menu_kb)
            await message.answer('Одобрено на бессрочно')
        else:
            print('Ошибка подтверждения')
            await message.answer('Произошла ошибка подтверждения платежа, попробуйте ещё раз.')
            return
    elif '-' in confirmation:
        print('NO')
        await bot.send_message(message.reply_to_message.forward_from.id,
                               'Мы не смогли проверить вашу оплату, свяжитесь с нами : @cryptolog_admin')


async def process_cancel_pending_payment(callback_query: types.CallbackQuery, state: FSMContext):
    await state.reset_state()
    print(get_info_about_user_callback(callback_query))
    await callback_query.message.edit_text(f"🤘 Выберите необходимый вам тариф:",
                                           reply_markup=rates_kb,
                                           parse_mode='Markdown')


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state='*')
    dp.register_message_handler(cmd_access, text="⭐️Тарифы", state='*')
    dp.register_message_handler(cmd_profile, text="👤 Ваш профиль", state='*')
    dp.register_message_handler(cmd_benefit, text="📋 Что вы получаете", state='*')
    dp.register_message_handler(cmd_stats, text="📊 Статистика автора", state='*')
    dp.register_message_handler(cmd_check_subs, commands="subs", is_admin=True, state='*')
    dp.register_message_handler(cmd_delete_subs, commands="delete", is_admin=True, state='*')
    dp.register_callback_query_handler(process_benefit, lambda c: c.data == 'access_btn', state='*')

    dp.register_callback_query_handler(process_three_month, lambda c: c.data == 'three_month', state='*')
    dp.register_callback_query_handler(process_one_year, lambda c: c.data == 'one_year', state='*')
    dp.register_callback_query_handler(process_indefinitely, lambda c: c.data == 'indefinitely', state='*')

    dp.register_callback_query_handler(process_pending_payment, lambda c: c.data == 'pending_payment', state='*')

    dp.register_callback_query_handler(process_cancel_pending_payment, lambda c: c.data == 'cancel_pending_payment',
                                       state=PaymentStage.waiting_for_pending)

    dp.register_message_handler(cmd_get_photo, content_types=types.ContentType.ANY,
                                state=PaymentStage.waiting_for_pending)

    dp.register_message_handler(cmd_get_confirmation, is_admin=True, state='*')
