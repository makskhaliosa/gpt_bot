import os
import logging
from logging.handlers import RotatingFileHandler
from random import randint

import openai
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
    dbpost_tg_user, dbpost_user_message, dbpost_gpt_message)
from payment_handlers import (
    buy_day_callback, buy_week_callback, buy_month_callback,
    precheckout_callback, successful_payment_callback, donation_info)
from training_handlers import (
    brainstorm_training, text_work_training, translation_work_training,
    education_training, free_talk_training, grammar_check_training)
from openai_module import (
    get_turbo_response, parse_gpt_response, get_text_from_voice, create_image)

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_TOKEN = os.getenv('OPENAI_API_KEY_DIANA')
openai.api_key = OPENAI_API_TOKEN
SASHA_SUPPORT = os.getenv('SASHA_SUPPORT')

# POST Creates a completion for the provided prompt and parameters
COMPLETION_ENDPOINT = 'https://api.openai.com/v1/completions/'
HEADERS = {'Authorization': f'Bearer {OPENAI_API_TOKEN}'}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# handler1 = FileHandler()
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

BASE_DIR = os.getcwd()


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
        response = await get_turbo_response(prompt, user)
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


async def audio_msg(update, context):
    try:
        user = update.message.from_user
        last_message = await update.message.reply_text(
            text=request_accepted_msg())
        ogg_ext = 'ogg'
        mp3_ext = 'mp3'
        filename = f'{BASE_DIR}/audio/voice_{randint(1, 9999999)}.'
        voice = await update.message.voice.get_file()
        await voice.download_to_drive(filename + ogg_ext)
        logger.debug(f'Voice сохранен. Тип - {update.message.voice.mime_type}')
        prompt = get_text_from_voice(filename, ogg_ext, mp3_ext)
        response = await get_turbo_response(prompt, user)
        text = parse_gpt_response(response)
        await update.message.reply_text(text=text)
        await last_message.delete()
        os.remove(filename + ogg_ext)
        dbpost_tg_user(update, user, response)
        user_msg = dbpost_user_message(update, prompt, user)
        dbpost_gpt_message(response, text, user_msg)
        logger.debug('Voice обработан.')
    except Exception as err:
        logger.error(f'Ошибка при обработке аудиосообщения: {err}')


async def send_image(update, context):
    try:
        user = update.message.from_user
        last_message = await update.message.reply_text(
            text=request_accepted_msg())
        msg: str = update.message.text
        prompt = msg.replace('Нарисуй картину ', '')
        response = await create_image(prompt)
        image_url = response['data'][0]['url']
        await update.message.reply_photo(photo=image_url)
        await last_message.delete()
        dbpost_tg_user(update, user, response)
        user_msg = dbpost_user_message(update, prompt, user)
        dbpost_gpt_message(response, image_url, user_msg)
        logger.debug('Картинка отправлена.')
    except Exception as err:
        logger.error(f'Ошибка при создании картинки: {err}')

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
            filters.Regex('^Нарисуй картину .*$'), send_image))
        application.add_handler(MessageHandler(
            filters.VOICE, audio_msg))
        application.add_handler(MessageHandler(
            filters.TEXT, send_gpt_response))
        application.add_handler(MessageHandler(
            filters.PHOTO, send_gpt_response))
        application.run_polling()
    except Exception as err:
        logger.error(f'Ошибка: {err}')


if __name__ == '__main__':
    main()
