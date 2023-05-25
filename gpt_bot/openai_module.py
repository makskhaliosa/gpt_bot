import os
import logging
from logging.handlers import RotatingFileHandler

import openai
#import whisper
from dotenv import load_dotenv
#from pydub import AudioSegment

from db_managers import dbget_gpt_message

load_dotenv()

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

OPENAI_API_TOKEN = os.getenv('OPENAI_API_KEY_DIANA')
openai.api_key = OPENAI_API_TOKEN

GPT_MODELS = {
    'turbo': 'gpt-3.5-turbo',
    'davinci': 'text-davinci-003',
    'gpt-4': 'gpt-4-32k-0314'
}


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


async def get_turbo_response(prompt, user):
    """
    Отправляет запрос (создает Completion) и возвращает ответ чата GPT turbo.
    """
    try:
        gpt_model = GPT_MODELS['turbo']
        temperature = 1
        last_gpt_response = dbget_gpt_message(user)
        if last_gpt_response:
            last_msg = last_gpt_response
        else:
            last_msg = 'Без контекста'
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


def get_text_from_voice(filename, extension1, extension2):
    """Расшифровывает аудиосообщение."""
    try:
        filename_mp3 = filename + extension2
        logger.info('Сохраняю сообщение в формате mp3')
        AudioSegment.from_file(filename + extension1).export(
            filename_mp3, format=extension2)
        logger.info('Сообщение сохранено. Начинаю расшифровку...')
        transcript = whisper.load_model('small').transcribe(filename_mp3)
        logger.info(
            f'Голосовое сообщение расшифровано. Text: {transcript["text"]}')
        return transcript['text']
    except Exception as err:
        logger.error(
            f'Ошибка при обработке голосового сообщения: {err}', exc_info=True)


async def create_image(prompt):
    """Создает картинку из запроса пользователя."""
    try:
        logger.info('Создаем картинку...')
        response = await openai.Image.acreate(prompt=prompt, n=1, size='512x512')
        logger.info('Картинка создана!')
        # получить url: response['data'][0]['url']
        return response
    except Exception as err:
        logger.error(f'Ошибка при получении картинки: {err}')
