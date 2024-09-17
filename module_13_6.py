# -*- coding: utf-8 -*-
# module_13_6.py
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import asyncio

api = "ABCDEF"
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


# Инициализируем "ОБЫЧНУЮ" клавиатуру, которая подстраивается под размеры интерфейса устройства
kb = ReplyKeyboardMarkup(resize_keyboard=True)
# Кнопки на клавиатуре, в один ряд
button1 = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
kb.row(button1, button2)
# Инициализируем "INLINE" клавиатуру, которая подстраивается под размеры интерфейса устройства
kb2 = InlineKeyboardMarkup()
# Кнопки на клавиатуре, в один ряд
button3 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button4 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb2.row(button3, button4)


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Ну что ж, пожалуй приступим!', reply_markup=kb)  # Показать клавиатуру


# ------------------------------------------
@dp.message_handler(text=['информация', 'Информация', 'ИНФОРМАЦИЯ'])
async def information(message):
    await message.answer('Привет! Я бот, помогающий твоему здоровью.')


@dp.message_handler(text=['рассчитать', 'Рассчитать', 'РАССЧИТАТЬ'])
async def set_age(message):
    await message.answer('Выберите опцию:', reply_markup=kb2)  # Показать клавиатуру


# ------------------------------------------
# Обработчик callback-запроса с callback_data 'formulas'
@dp.callback_query_handler(text='formulas')
async def get_formulas(call):   # : types.CallbackQuery
    await call.message.answer('Формула Миффлина-Сан Жеора')
    await call.message.answer("Для мужчины: \n10 * weight + 6.25 * growth - 5 * age + 5")
    await call.message.answer("Для женщины: \n10 * weight + 6.25 * growth - 5 * age - 161")
    await call.answer(text='abcd')  # Завершение вызова


# Обработчик callback-запроса с callback_data 'calories'
@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await call.answer(text='abcd')  # Завершение вызова
    await UserState.age.set()


# ------------------------------------------

# Обработчик машины состояний: UserState.age
@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age1=message.text)
    data = await state.get_data()
    await message.answer(f"Получено: ваш возраст = {data['age1']}")
    await message.answer('Введите свой рост:')
    await UserState.growth.set()


# Обработчик машины состояний: UserState.growth
@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth1=message.text)
    data = await state.get_data()
    await message.answer(f"Получено: ваш рост = {data['growth1']}")
    await message.answer('Введите свой вес:')
    await UserState.weight.set()


# Обработчик машины состояний: UserState.weight
# И собственно расчёт по формуле Миффлина-Сан Жеора
@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight1=message.text)
    data = await state.get_data()
    await message.answer(f"Получено: ваш вес = {data['weight1']} ")
    # Расчёт калорий по формуле Миффлина-Сан Жеора
    w1 = float(data['weight1'])  # Вес
    g1 = float(data['growth1'])  # Рост
    a1 = float(data['age1'])  # Возраст
    calories_male = 10 * w1 + 6.25 * g1 - 5 * a1 + 5
    calories_female = 10 * w1 + 6.25 * g1 - 5 * a1 - 161
    # Выдаём результат вычислений
    await message.answer(f"Расчёт калорий для оптимального похудения или сохранения нормального веса")
    await message.answer(f"по формуле Нефелина-Сан Жеора")
    await message.answer(f"Для мужчины: \n10 * {w1} + 6.25 * {g1} - 5 * {a1} + 5 = {calories_male}")
    await message.answer(f"Для женщины: \n10 * {w1} + 6.25 * {g1} - 5 * {a1} - 161 = {calories_female}")
    await message.answer(
        "В принципе, это всё, что вам нужно знать, — \nДля оптимального похудения или сохранения нормального веса")
    await state.finish()


@dp.message_handler()  # Прочие неопознанные сообщения от человека
async def all_message(message):
    await message.answer(message.text)  # Отправим человеку его же сообщение обратно
    await message.answer("Введите команду /start чтобы начать общение")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
