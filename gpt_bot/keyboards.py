import os

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)
from dotenv import load_dotenv

load_dotenv()

SASHA_SUPPORT = os.getenv('SASHA_SUPPORT')
DONATION_LINK = os.getenv('DONATION_LINK')

# Название кнопок в телеграме и pattern в callback_data
# Информация об обучении
START_TRAINING = 'Пройти обучение'
START_CHAT = 'Перейти к чату'
START_BRAINSTORM = 'Мозговой штурм'
TEXT_WORK = 'Текстовая работа'
TRANSLATION_WORK = 'Переводчик'
EDUCATION = 'Обучение'
GRAMMAR_CHECK = 'Исправление грамматики'
FREE_TALK = 'Свободное общение'
# FEEDBACK = 'Обратная связь'

# Информация об оплате
PAYMENT_INFO = 'Тарифы и способы оплаты'
DAY_TARIFF = 'Купить день'
WEEK_TARIFF = 'Купить неделю'
MONTH_TARIFF = 'Купить месяц'
DONATE_INFO = 'Поддержать проект'
DONATE = 'Отправить деньги'

# Общее
SUPPORT = 'Помощь/Обратная связь'
WRITE_TO_SASHA = 'Написать нам'
BACK_TO_MENU = 'Назад к чату'

# Кнопки для строковых клавиатур
inl_keyboard_start = [
    [
        InlineKeyboardButton(START_TRAINING, callback_data=START_TRAINING),
        InlineKeyboardButton(START_CHAT, callback_data=START_CHAT),
    ]
]
inl_keyboard_training = [
    [InlineKeyboardButton(START_BRAINSTORM, callback_data=START_BRAINSTORM)],
    [InlineKeyboardButton(TEXT_WORK, callback_data=TEXT_WORK)],
    [InlineKeyboardButton(TRANSLATION_WORK, callback_data=TRANSLATION_WORK)],
    [InlineKeyboardButton(EDUCATION, callback_data=EDUCATION)],
    [InlineKeyboardButton(GRAMMAR_CHECK, callback_data=GRAMMAR_CHECK)],
    [InlineKeyboardButton(FREE_TALK, callback_data=FREE_TALK)],
]
inl_keyboard_brainstorm = [
    [InlineKeyboardButton(START_CHAT, callback_data=START_CHAT)],
    [InlineKeyboardButton(TEXT_WORK, callback_data=TEXT_WORK)],
    [InlineKeyboardButton(TRANSLATION_WORK, callback_data=TRANSLATION_WORK)],
    [InlineKeyboardButton(EDUCATION, callback_data=EDUCATION)],
    [InlineKeyboardButton(GRAMMAR_CHECK, callback_data=GRAMMAR_CHECK)],
    [InlineKeyboardButton(FREE_TALK, callback_data=FREE_TALK)],
]
inl_keyboard_text_work = [
    [InlineKeyboardButton(START_CHAT, callback_data=START_CHAT)],
    [InlineKeyboardButton(START_BRAINSTORM, callback_data=START_BRAINSTORM)],
    [InlineKeyboardButton(TRANSLATION_WORK, callback_data=TRANSLATION_WORK)],
    [InlineKeyboardButton(EDUCATION, callback_data=EDUCATION)],
    [InlineKeyboardButton(GRAMMAR_CHECK, callback_data=GRAMMAR_CHECK)],
    [InlineKeyboardButton(FREE_TALK, callback_data=FREE_TALK)],
]
inl_keyboard_translation_work = [
    [InlineKeyboardButton(START_CHAT, callback_data=START_CHAT)],
    [InlineKeyboardButton(START_BRAINSTORM, callback_data=START_BRAINSTORM)],
    [InlineKeyboardButton(TEXT_WORK, callback_data=TEXT_WORK)],
    [InlineKeyboardButton(EDUCATION, callback_data=EDUCATION)],
    [InlineKeyboardButton(GRAMMAR_CHECK, callback_data=GRAMMAR_CHECK)],
    [InlineKeyboardButton(FREE_TALK, callback_data=FREE_TALK)],
]
inl_keyboard_education = [
    [InlineKeyboardButton(START_CHAT, callback_data=START_CHAT)],
    [InlineKeyboardButton(START_BRAINSTORM, callback_data=START_BRAINSTORM)],
    [InlineKeyboardButton(TEXT_WORK, callback_data=TEXT_WORK)],
    [InlineKeyboardButton(TRANSLATION_WORK, callback_data=TRANSLATION_WORK)],
    [InlineKeyboardButton(GRAMMAR_CHECK, callback_data=GRAMMAR_CHECK)],
    [InlineKeyboardButton(FREE_TALK, callback_data=FREE_TALK)],
]
inl_keyboard_grammar_check = [
    [InlineKeyboardButton(START_CHAT, callback_data=START_CHAT)],
    [InlineKeyboardButton(START_BRAINSTORM, callback_data=START_BRAINSTORM)],
    [InlineKeyboardButton(TEXT_WORK, callback_data=TEXT_WORK)],
    [InlineKeyboardButton(TRANSLATION_WORK, callback_data=TRANSLATION_WORK)],
    [InlineKeyboardButton(EDUCATION, callback_data=EDUCATION)],
    [InlineKeyboardButton(FREE_TALK, callback_data=FREE_TALK)],
]
inl_keyboard_free_talk = [
    [InlineKeyboardButton(START_CHAT, callback_data=START_CHAT)],
    [InlineKeyboardButton(START_BRAINSTORM, callback_data=START_BRAINSTORM)],
    [InlineKeyboardButton(TEXT_WORK, callback_data=TEXT_WORK)],
    [InlineKeyboardButton(TRANSLATION_WORK, callback_data=TRANSLATION_WORK)],
    [InlineKeyboardButton(EDUCATION, callback_data=EDUCATION)],
    [InlineKeyboardButton(GRAMMAR_CHECK, callback_data=GRAMMAR_CHECK)],
]
inl_keyboard_donate = [
    [InlineKeyboardButton(DONATE, url=DONATION_LINK)],
    [InlineKeyboardButton(START_TRAINING, callback_data=START_TRAINING)],
    [InlineKeyboardButton(SUPPORT, url=SASHA_SUPPORT)],
    [InlineKeyboardButton(BACK_TO_MENU, callback_data=BACK_TO_MENU)]
]
inl_keyboard_support = [
    [InlineKeyboardButton(WRITE_TO_SASHA, url=SASHA_SUPPORT)],
    [InlineKeyboardButton(BACK_TO_MENU, callback_data=BACK_TO_MENU)]
]
# Строковые клавиатуры
markup_start = InlineKeyboardMarkup(inl_keyboard_start)
markup_training = InlineKeyboardMarkup(inl_keyboard_training)
markup_brainstorm = InlineKeyboardMarkup(inl_keyboard_brainstorm)
markup_textwork = InlineKeyboardMarkup(inl_keyboard_text_work)
markup_translationwork = InlineKeyboardMarkup(inl_keyboard_translation_work)
markup_education = InlineKeyboardMarkup(inl_keyboard_education)
markup_grammarcheck = InlineKeyboardMarkup(inl_keyboard_grammar_check)
markup_freetalk = InlineKeyboardMarkup(inl_keyboard_free_talk)
markup_donate = InlineKeyboardMarkup(inl_keyboard_donate)
markup_support = InlineKeyboardMarkup(inl_keyboard_support)

# Кнопки для клавиатур меню
reply_keyboard_gpt_response = [
    [START_TRAINING, SUPPORT],
    [DONATE_INFO]
]
reply_keyboard_tariffsandpayments = [
    [DAY_TARIFF, WEEK_TARIFF, MONTH_TARIFF],
    [SUPPORT]
]
# Клавиатуры меню
reply_markup_gpt_response = ReplyKeyboardMarkup(
                                reply_keyboard_gpt_response,
                                resize_keyboard=True,
                                one_time_keyboard=True
                            )
reply_markup_tariffsandpayments = ReplyKeyboardMarkup(
                                     reply_keyboard_tariffsandpayments,
                                     resize_keyboard=True,
                                     one_time_keyboard=True
                                  )
