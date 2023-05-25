import os, logging, sys
from logging import StreamHandler

from telegram import (LabeledPrice)
from dotenv import load_dotenv

from bots_messages import pay_bot_img, DONATIONINFO_TEXT
from keyboards import markup_donate
from db_managers import dbpost_payment

load_dotenv()

PAYMENT_PROVIDER_TOKEN = os.getenv('PAYMENT_PROVIDER_TOKEN')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = StreamHandler(stream=sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s, %(levelname)s, %(name)s, '
    '%(lineno)s, %(funcName)s, %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

async def buy_day_callback(update, context):
    """Отправляет счет на день."""
    try:
        chat_id = update.message.chat_id
        title = 'Бот на день'
        description = ('Можно пользоваться ботом в течение 24 '
                       'часов без ограничений.')
        payload = 'GPT bot'
        provider_token = PAYMENT_PROVIDER_TOKEN
        currency = 'RUB'
        price = 50
        # Стоимость умножаем на 100, чтобы в ТГ отображалось 2 цифры
        # после запятой
        prices = [LabeledPrice('Доступ к боту на 24 часа', price * 100)]
        start_parameter = 'https://t.me/gedzi_bot?start=new_request'
        photo_url = pay_bot_img
        await context.bot.send_invoice(
            chat_id, title, description, payload, provider_token, currency,
            prices, photo_url=photo_url, photo_width=320, photo_height=320)
        logger.debug('Тариф на день отправлен.')
    except Exception as err:
        logger.error(f'Ошибка обработки тарифа на день: {err}')


async def buy_week_callback(update, context):
    """Отправляет счет на неделю."""
    try:
        chat_id = update.message.chat_id
        title = 'Бот на неделю'
        description = ('Можно пользоваться ботом\n'
                       '7 дней без ограничений.')
        payload = 'GPT bot'
        provider_token = PAYMENT_PROVIDER_TOKEN
        currency = 'RUB'
        price = 1000
        # Стоимость умножаем на 100, чтобы в ТГ отображалось 2 цифры
        # после запятой
        prices = [LabeledPrice('Доступ к боту на 7 дней', price * 100)]
        photo_url = pay_bot_img
        await context.bot.send_invoice(
            chat_id, title, description, payload, provider_token, currency,
            prices, photo_url=photo_url, photo_width=320, photo_height=320)
        logger.debug('Тариф на неделю отправлен.')
    except Exception as err:
        logger.error(f'Ошибка обработки тарифа на неделю: {err}')


async def buy_month_callback(update, context):
    """Отправляет счет на месяц."""
    try:
        chat_id = update.message.chat_id
        title = 'Бот на месяц'
        description = ('Можно пользоваться ботом в течение 30 дней '
                       'без ограничений.')
        payload = 'GPT bot'
        provider_token = PAYMENT_PROVIDER_TOKEN
        currency = 'RUB'
        price = 2000
        prices = [LabeledPrice('Доступ к боту на 30 дней', price * 100)]
        photo_url = pay_bot_img
        await context.bot.send_invoice(
            chat_id, title, description, payload, provider_token, currency,
            prices, photo_url=photo_url, photo_width=320, photo_height=320)
        logger.debug('Тариф на месяц отправлен.')
    except Exception as err:
        logger.error(f'Ошибка обработки тарифа на месяц: {err}')


async def precheckout_callback(update, context):
    """
    Отвечает на запрос PreQecheckoutQuery после нажатия на
    кнопку 'заплатить'.
    """
    try:
        query = update.pre_checkout_query
        # check the payload, is this from your bot?
        if query.invoice_payload != 'GPT bot':
            # answer False pre_checkout_query
            await query.answer(ok=False, error_message='Ошибка при запросе.')
            logger.info('Payload не соответствует нашему.')
        await query.answer(ok=True)
        logger.debug('Запрос на платеж принят.')
    except Exception as err:
        logger.error(f'Ошибка при обработке запроса платежа: {err}')


async def successful_payment_callback(update, context):
    """
    Вносит информацию об оплате в базу данных и
    отправляет сообщение об успешной оплате.
    """
    try:
        payment_info = update.message.successful_payment
        dbpost_payment(update, payment_info)
        await update.message.reply_text(
            'Благодарим за оплату! '
            'Теперь бот готов творить и создавать!')
        logger.debug('Платеж успешно пройден.')
    except Exception as err:
        logger.error(f'Ошибка при отрпавке сообщения об оплате: {err}')


async def donation_info(update, context):
    """Отправляет текст и кнопки для донейшн."""
    try:
        await update.message.reply_text(
            text=DONATIONINFO_TEXT,
            reply_markup=markup_donate
        )
        logger.debug('Информация о данейшн отправлена.')
    except Exception as err:
        logger.error(f'Ошибка при отправке инфы о донейшн: {err}')
