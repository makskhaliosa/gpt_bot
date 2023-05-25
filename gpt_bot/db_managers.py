import os
import requests
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv('BASE_URL')

TG_USERS_URL = fr'{BASE_URL}/api/v1/tg_users/'
TARIFFS_URL = fr'{BASE_URL}/api/v1/tariffs/'
GPT_MESSAGES_URL = fr'{BASE_URL}/api/v1/gpt_messages/'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(
    'gpt_chat_log.log',
    maxBytes=50000000,
    backupCount=5,
    encoding='utf-8'
)
# StreamHandler(stream=sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s, %(levelname)s, %(name)s, '
    '%(lineno)s, %(funcName)s, %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def dbpost_tg_user(update, user, response):
    """POST запрос на создание пользователя ТГ."""
    try:
        # params = {"search": username}
        chat = update.effective_chat
        total_tokens = response.usage.get('total_tokens')
        if not total_tokens:
            total_tokens = 100
        data = {
            "chat_id": chat.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "tokens_used": total_tokens
        }
        username = data['username']
        r_get = requests.get(f'{TG_USERS_URL}{username}/')
        logger.debug('Проверяю пользователя...')
        if 'detail' not in r_get.json():
            logger.debug('Пользователь найден.')
            # tg_user_id = r_get.json()[0]['id']
            tokens_before = r_get.json().get('tokens_used')
            tokens_after = tokens_before + data['tokens_used']
            tokens_info = {"tokens_used": tokens_after}
            r_patch = requests.patch(
                f'{TG_USERS_URL}{username}/', data=tokens_info)
            logger.debug('Пользователь обновлен!')
            return r_patch.json()
        else:
            r_post = requests.post(TG_USERS_URL, data=data)
            logger.debug('Пользователь записан в базу данных.')
            return r_post.json()
    except Exception as err:
        logger.error(
            f'Ошибка при запросе к базе данных для пользователя: {err}',
            exc_info=True)


def dbget_tg_user(username):
    """GET запрос по username пользователя из базы данных."""
    response = requests.get(f'{TG_USERS_URL}{username}/')
    return response.json()


def dbpost_user_message(update, text, user):
    try:
        message_id = update.message.message_id
        date = update.message.date
        data = {
            'message_id': message_id,
            'date': date,
            'text': text
        }
        username = user.username
        logger.debug('Записываю сообщение пользователя...')
        r_post = requests.post(
            f'{TG_USERS_URL}{username}/user_messages/',
            data=data
        )
        logger.debug('Сообщение пользователя записано!')
        return r_post.json()
    except Exception as err:
        logger.error(
            f'Ошибка при запросе к базе данных для сообщения: {err}',
            exc_info=True)


def dbget_gpt_message(user):
    try:
        username = user.username
        logger.debug('Получаю последнее сообщение чатаGPT...')
        last_message = requests.get(
            f'{TG_USERS_URL}{username}/user_messages/')
        logger.debug('Сообщение чатаGPT получено.')
        if last_message.json()[-1].get('gpt_response'):
            return last_message.json()[-1].get('gpt_response').get('text')
    except Exception as err:
        logger.error(
            f'Ошибка при получении сообщения: {err}',
            exc_info=True)


def dbpost_gpt_message(response, text, user_msg):
    try:
        message_id = response.get('id')
        date = datetime.fromtimestamp(response.get('created'))
        gpt_model = response.get('model')
        if not gpt_model:
            gpt_model = 'image'
        total_tokens = response.usage.get('total_tokens')
        if not total_tokens:
            total_tokens = 100
        data = {
            'user_message': user_msg['message_id'],
            'message_id': message_id,
            'date': date,
            'gpt_model': gpt_model,
            'total_tokens': total_tokens,
            'text': text
        }
        logger.debug(f'Записываю сообщение gpt...')
        r_post = requests.post(
            GPT_MESSAGES_URL,
            data=data
        )
        logger.debug(f'Сообщение gpt записано!')
        return r_post.json()
    except Exception as err:
        logger.error(
            f'Ошибка при запросе к базе данных для сообщения gpt: {err}',
            exc_info=True)


def dbpost_payment(update, payment_info):
    try:
        tg_payment_id = payment_info.telegram_payment_charge_id
        bank_payment_id = payment_info.provider_payment_charge_id
        amount = int(payment_info.total_amount/100)
        currency = payment_info.currency
        username = update.message.from_user.username
        tariff = requests.get(f'{TARIFFS_URL}{amount}/').json()
        data = {
            'tg_payment_id': tg_payment_id,
            'bank_payment_id': bank_payment_id,
            'amount': amount,
            'currency': currency,
            'tariff': tariff['name']
        }
        logger.debug(f'Записываю информацию об оплате... {data}')
        r_post = requests.post(
            f'{TG_USERS_URL}{username}/payments/', data=data)
        logger.debug(f'Информация об оплате записана!')
        return r_post.json()
    except Exception as err:
        logger.error(
            f'Ошибка при записи информации об оплате: {err}', exc_info=True)
