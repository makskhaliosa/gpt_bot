import os
import sys
import requests
import logging
from logging.handlers import RotatingFileHandler
from random import randint

import openai
from telegram import (
    ReplyKeyboardMarkup, ReplyKeyboardRemove,
    Update
)
from telegram.ext import (
    Application, filters, CallbackQueryHandler,
    CommandHandler, MessageHandler, PreCheckoutQueryHandler)
from dotenv import load_dotenv

from bots_messages import (
    GREETING_TEXT, TRAINING_OPTIONS, SUPPORT_TEXT,
    PAYMENTMETHODS_TEXT, REQUEST_ACCEPTED_MESSAGES, STARTCHAT_TEXT)
from keyboards import (
    markup_start, markup_training, reply_markup_gpt_response,
    reply_markup_tariffsandpayments, markup_support,
    START_BRAINSTORM, START_CHAT, START_TRAINING, TEXT_WORK,
    TRANSLATION_WORK, EDUCATION, GRAMMAR_CHECK, FREE_TALK, SUPPORT,
    PAYMENT_INFO, WEEK_TARIFF, DAY_TARIFF, MONTH_TARIFF, DONATE_INFO, DONATE,
    BACK_TO_MENU)
from db_managers import (
    dbpost_tg_user, dbget_tg_user, dbpost_user_message, dbpost_gpt_message,
    dbget_gpt_message)
from payment_handlers import (
    buy_day_callback, buy_week_callback, buy_month_callback,
    precheckout_callback, successful_payment_callback, donation_info)
from training_handlers import (
    brainstorm_training, text_work_training, translation_work_training,
    education_training, free_talk_training, grammar_check_training)

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_TOKEN = os.getenv('OPENAI_API_KEY_DIANA')
openai.api_key = OPENAI_API_TOKEN
GPT_MODELS = {
    'turbo': 'gpt-3.5-turbo',
    'davinci': 'text-davinci-003'
}
SASHA_SUPPORT = os.getenv('SASHA_SUPPORT')

# POST Creates a completion for the provided prompt and parameters
COMPLETION_ENDPOINT = 'https://api.openai.com/v1/completions/'
HEADERS = {'Authorization': f'Bearer {OPENAI_API_TOKEN}'}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(
    'gpt_chat_log.log',
    maxBytes=50000000,
    backupCount=5,
    encoding='utf-8'
)
formatter = logging.Formatter(
    '%(asctime)s, %(levelname)s, %(name)s, '
    '%(lineno)s, %(funcName)s, %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


async def wake_up(update, context):
    """Начинает диалог с пользователем после команды start."""
    try:
        name = update.message.chat.first_name
        await update.message.reply_text(
            text=f'{name}, ' + GREETING_TEXT,
            reply_markup=markup_start
        )
    except Exception as err:
        logger.error(f'Проблема со стартовым сообщением в чате телеги: {err}')


async def start_training(update, context):
    """Начинает блок обучения пользователя (инлайн кнопка под сообщением)."""
    try:
        query = update.callback_query
        await query.answer()
        await query.message.reply_text(
            text=TRAINING_OPTIONS,
            reply_markup=markup_training
        )
        logger.debug('Описание обучения отправлено.')
    except Exception as err:
        logger.error(f'Ошибка с передачей описания обучения: {err}')


async def start_chat_button(update, context):
    """Обрабатывает кнопку "Перейти к чату" в блоке обучения."""
    try:
        query = update.callback_query
        await query.answer()
        await query.message.reply_text(
            text=STARTCHAT_TEXT,
            reply_markup=reply_markup_gpt_response
        )
        logger.debug('start_chat отправлен.')
    except Exception as err:
        logger.error(f'Ошибка при передаче start_chat: {err}')


async def start_training_over(update, context):
    """Начинает блок с обучением пользователя (кнопка внизу экрана)."""
    try:
        await update.message.reply_text(
            text=TRAINING_OPTIONS,
            reply_markup=markup_training
        )
        logger.debug('Повторное обучение успешно начато.')
    except Exception as err:
        logger.error(f'Ошибка при повторном начале обучения: {err}')


async def get_davinci_response(prompt):
    """
    Отправляет запрос (создает Completion)
    и возвращает ответ чата GPT davinci.
    """
    try:
        gpt_model = GPT_MODELS['davinci']
        max_tokens = 4000
        temperature = 1
        top_p = 1
        n = 1
        data = {
            'model': gpt_model,
            'prompt': prompt,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'top_p': top_p,
            'n': n
        }
        logger.debug('Отправляю запрос в chat-gpt.')
        response = await openai.Completion.acreate(**data)
        logger.debug('Запрос успешно отправлен.')
        return response
    except Exception as err:
        logger.error(f'Проблема с запросом к апи: {err}')


async def get_turbo_response(prompt, last_msg='No message'):
    """
    Отправляет запрос (создает Completion) и возвращает ответ чата GPT turbo.
    """
    try:
        gpt_model = GPT_MODELS['turbo']
        temperature = 1
        data = {
            'model': gpt_model,
            'messages': [
                # {'role': 'system', 'content': 'You need to speak spoken language.'},
                {'role': 'user', 'content': prompt},
                {'role': 'assistant', 'content': last_msg}
            ],
            'temperature': temperature
        }
        logger.debug('Отправляю запрос в chat-gpt.')
        response = await openai.ChatCompletion.acreate(**data)
        logger.debug('Запрос успешно отправлен.')
        return response
    except Exception as err:
        logger.error(f'Проблема с запросом к апи: {err}')


def parse_gpt_response(response):
    """Возвращает обработанное сообщение из ответа от чата GPT."""
    try:
        # gpt-3 - text = response.choices[0].get('text')
        # chat-gpt
        text = response.choices[0].message.get('content')
        logger.debug('Текст ответа получен.')
        return text
    except Exception as err:
        logger.error(f'Проблема с получением текста ответа: {err}')


def request_accepted_msg():
    """
    Отправляет вспомогательное сообщение пользователю о получении
    запроса от пользователя.
    """
    try:
        num = randint(1, 10)
        msg = REQUEST_ACCEPTED_MESSAGES[num]
        logger.debug('Сообщение для бота получено.')
        return msg
    except TypeError as err:
        logger.error(f'Под таким номером нет сообщения для бота: {err}')


async def send_gpt_response(update, context):
    """
    Подставляет нужные данные в запрос к GPT и отправляет
    ответ в чат пользователю.
    """
    try:
        prompt = update.message.text
        user = update.message.from_user
        # photo_id = update.message.photo[-1].file_id
        # photo_file = await context.bot.get_file(photo_id)
        # photo_bytes = await photo_file.download_as_bytearray()
        # chat-gpt-turbo
        last_message = await update.message.reply_text(
            text=request_accepted_msg()
            #reply_markup=reply_markup_gpt_response
        )
        last_gpt_response = dbget_gpt_message(user)
        if last_gpt_response:
            response = await get_turbo_response(prompt, last_gpt_response)
        else:
            response = await get_turbo_response(prompt)
        text = parse_gpt_response(response)
        await update.message.reply_text(text=text)
        await last_message.delete()
        dbpost_tg_user(update, user, response)
        user_msg = dbpost_user_message(update, prompt, user)
        dbpost_gpt_message(response, text, user_msg)
        logger.debug('Сообщение отправлено пользователю!')
    except Exception as err:
        logger.error(f'Проблема с передачей сообщения в запрос к апи: {err}')


# payment section
async def tarifs_and_payment_info(update, context):
    """Отправляет информацию о тарифах и оплате."""
    await update.message.reply_text(
        text=PAYMENTMETHODS_TEXT,
        reply_markup=reply_markup_tariffsandpayments
    )


async def support(update, context):
    try:
        await update.message.reply_text(
            text=SUPPORT_TEXT,
            reply_markup=markup_support
        )
        logger.debug('Сообщение для связи отправлено')
    except Exception as err:
        logger.error(f'Ошибка при отправке сообщения для связи: {err}')


def main():
    """Запускает бота."""
    # bot = Bot(BOT_TOKEN)
    # queue = asyncio.Queue()
    # updater = Updater(BOT_TOKEN, update_queue=queue)
    application = Application.builder().token(BOT_TOKEN).build()
    try:
        application.add_handler(CommandHandler('start', wake_up))
        application.add_handler(CommandHandler('support', support))
        application.add_handler(CommandHandler('donate', donation_info))
        application.add_handler(CommandHandler('instructions', start_training_over))
        application.add_handler(MessageHandler(
            filters.Regex(f'^{SUPPORT}$'), support))
        # Обработчики раздела оплаты
        application.add_handler(MessageHandler(
            filters.Regex(f'^{PAYMENT_INFO}$'), tarifs_and_payment_info))
        application.add_handler(MessageHandler(
            filters.Regex(f'^{DAY_TARIFF}$'), buy_day_callback))
        application.add_handler(MessageHandler(
            filters.Regex(f'^{WEEK_TARIFF}$'), buy_week_callback))
        application.add_handler(MessageHandler(
            filters.Regex(f'^{MONTH_TARIFF}$'), buy_month_callback))
        application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
        application.add_handler(MessageHandler(
            filters.SUCCESSFUL_PAYMENT, successful_payment_callback))
        application.add_handler(MessageHandler(
            filters.Regex(f'^{DONATE_INFO}$'), donation_info))
        # Обработчики раздела обучения
        application.add_handler(
            CallbackQueryHandler(start_training, pattern=START_TRAINING))
        application.add_handler(MessageHandler(
            filters.Regex(f'^{START_TRAINING}$'), start_training_over))
        application.add_handler(
            CallbackQueryHandler(brainstorm_training, pattern=START_BRAINSTORM))
        application.add_handler(
            CallbackQueryHandler(text_work_training, pattern=TEXT_WORK))
        application.add_handler(
            CallbackQueryHandler(
                translation_work_training, pattern=TRANSLATION_WORK))
        application.add_handler(
            CallbackQueryHandler(education_training, pattern=EDUCATION))
        application.add_handler(
            CallbackQueryHandler(grammar_check_training, pattern=GRAMMAR_CHECK))
        application.add_handler(
            CallbackQueryHandler(free_talk_training, pattern=FREE_TALK))
        application.add_handler(
            CallbackQueryHandler(start_chat_button, START_CHAT))
        application.add_handler(
            CallbackQueryHandler(start_chat_button, BACK_TO_MENU))
        # Обработчики сообщений в чат GPT
        application.add_handler(MessageHandler(
            filters.TEXT, send_gpt_response))
        application.add_handler(MessageHandler(
            filters.PHOTO, send_gpt_response))
        application.run_polling()
    except Exception as err:
        logger.error(f'Ошибка: {err}')


if __name__ == '__main__':
    main()
