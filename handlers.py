from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
import random
import aiosqlite
from aiogram import Router

router = Router()

keyb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='1'), KeyboardButton(text='2')],
    [KeyboardButton(text='3'), KeyboardButton(text='4')]
], resize_keyboard=True, #"""Меняет кнопки до минимального значения"""
    one_time_keyboard=True,
    input_field_placeholder='Ваш ответ...'
)


CORRECT_ANSWER = None
ID_LIST = None
CORRECT_ANSWER_NUM = 0
NUMBER = 1


@router.message(Command('start'))
async def start(message: Message):
    await message.answer(f"<b>Добро пожаловать в Викторину.</b>"
                         f"\nВам будет задано 10 вопросов на общую эрудицию"
                         f"\n\nОсновные команды:"
                         f"\n/start - Начальное меню"
                         f"\n/play - Начать игру", parse_mode='html')


async def get_number_question():
    async with aiosqlite.connect('quiz.db') as db:
        async with db.execute('SELECT id FROM questions') as cursor:
            return await cursor.fetchall()


async def select_question():
    async with aiosqlite.connect('quiz.db') as db:
        global ID_LIST
        async with db.execute('SELECT * FROM questions WHERE id=?', ID_LIST[0]) as cursor:
            ID_LIST.pop(0)
            return await cursor.fetchone()


async def ask_question(message: Message):
    global CORRECT_ANSWER, NUMBER
    mes = await select_question()
    CORRECT_ANSWER = mes[6]
    await message.answer(f'Вопрос № {NUMBER}'
                         f'\n<b>{mes[1]}</b>'
                         f'\n1) {mes[2]}'
                         f'\n2) {mes[3]}'
                         f'\n3) {mes[4]}'
                         f'\n4) {mes[5]}', parse_mode='html', reply_markup=keyb)


@router.message(Command('play'))
async def play(message: Message):

    global ID_LIST, NUMBER, CORRECT_ANSWER_NUM
    ID_LIST = await get_number_question()
    random.shuffle(ID_LIST)
    NUMBER = 1
    CORRECT_ANSWER_NUM = 0

    await ask_question(message)


@router.message(lambda message: message.text in ['1', '2', '3', '4'])
async def process_answer(message: Message):
    global CORRECT_ANSWER, NUMBER, CORRECT_ANSWER_NUM
    NUMBER += 1
    if message.text == str(CORRECT_ANSWER):
        CORRECT_ANSWER_NUM += 1
    if NUMBER >= 11:
        await message.answer(f"Викторина завершена"
                             f"\nПравильных ответов {CORRECT_ANSWER_NUM}"
                             f"\n/start - Начальное меню"
                             f"\n/play - Начать игру заново"
                             )
        return False

    await ask_question(message)
