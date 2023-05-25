import sys, logging
from logging import StreamHandler

from keyboards import (
    markup_brainstorm, markup_textwork, markup_education,
    markup_freetalk, markup_grammarcheck, markup_translationwork)
from bots_messages import (
    BRAINSTORM_TEXT, TEXTWORK_TEXT, TRANSLATIONWORK_TEXT,
    GRAMMARCHECK_TEXT, FREETALK_TEXT, EDUCATION_TEXT)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = StreamHandler(stream=sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s, %(levelname)s, %(name)s, '
    '%(lineno)s, %(funcName)s, %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

async def brainstorm_training(update, context):
    """Отправляет блок обучения "Мозговой штурм"."""
    try:
        query = update.callback_query
        await query.answer()
        await query.message.edit_text(
            text=BRAINSTORM_TEXT,
            reply_markup=markup_brainstorm
        )
        logger.debug('brainstorm отправлен.')
    except Exception as err:
        logger.error(f'Ошибка в теме brainstorm: {err}')


async def text_work_training(update, context):
    """Отправляет блок обучения "Работа с текстом"."""
    try:
        query = update.callback_query
        await query.answer()
        await query.message.edit_text(
            text=TEXTWORK_TEXT,
            reply_markup=markup_textwork
        )
        logger.debug('text_work отправлен.')
    except Exception as err:
        logger.error(f'Ошибка в теме text_work: {err}')


async def translation_work_training(update, context):
    """Отправляет блок обучения "Перевод текста"."""
    try:
        query = update.callback_query
        await query.answer()
        await query.message.edit_text(
            text=TRANSLATIONWORK_TEXT,
            reply_markup=markup_translationwork
        )
        logger.debug('translation_work отправлен.')
    except Exception as err:
        logger.error(f'Ошибка в теме translation_work: {err}')


async def education_training(update, context):
    """Отправляет блок обучения "Обучение"."""
    try:
        query = update.callback_query
        await query.answer()
        await query.message.edit_text(
            text=EDUCATION_TEXT,
            reply_markup=markup_education
        )
        logger.debug('education отправлен.')
    except Exception as err:
        logger.error(f'Ошибка в теме education: {err}')


async def grammar_check_training(update, context):
    """Отправляет блок обучения "Исправление грамматики"."""
    try:
        query = update.callback_query
        await query.answer()
        await query.message.edit_text(
            text=GRAMMARCHECK_TEXT,
            reply_markup=markup_grammarcheck
        )
        logger.debug('grammar_check отправлен.')
    except Exception as err:
        logger.error(f'Ошибка в теме grammar_check: {err}')


async def free_talk_training(update, context):
    """Отправляет блок обучения "Свободное общение"."""
    try:
        query = update.callback_query
        await query.answer()
        await query.message.edit_text(
            text=FREETALK_TEXT,
            reply_markup=markup_freetalk
        )
        logger.debug('free_talk отправлен.')
    except Exception as err:
        logger.error(f'Ошибка в теме free_talk: {err}')
