import logging
from aiogram import Bot, Dispatcher, types
import sqlite3
import aiosqlite
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import filters

# Вставь свой токен бота
TOKEN = "7400929027:AAGm61oA8jqTWatoq4yaDDX2SmAOWP59kYE"

# Вопросы и ответы
FAQ = {
    "как сделать заказ": "Вы можете сделать заказ на нашем сайте, выбрав товар и нажав кнопку 'Купить'.",
    "как оплатить": "Мы принимаем оплату картой, через СБП и электронные кошельки.",
    "где мой заказ": "Укажите номер заказа, и мы уточним статус доставки.",
    "что делать если товар не пришел": "Напишите нам номер заказа, мы проверим информацию и поможем."
}

# Кнопки
kb = ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(KeyboardButton("Задать вопрос"), KeyboardButton("Частые вопросы"))

# Логирование
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Инициализация базы данных
async def init_db():
    async with aiosqlite.connect("support.db") as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            message TEXT,
            department TEXT
        )
        """)
        await db.commit()

# Обработка команды /start
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.answer("Привет! Я бот поддержки магазина 'Продаем все на свете'. Чем могу помочь?", reply_markup=kb)

# Частые вопросы
@dp.message_handler(lambda msg: msg.text.lower() == "частые вопросы")
async def faq(message: types.Message):
    response = "\n\n".join([f"- {q.capitalize()}?\n  {a}" for q, a in FAQ.items()])
    await message.answer(f"Вот список частых вопросов:\n\n{response}")

# Задать вопрос
@dp.message_handler(lambda msg: msg.text.lower() == "задать вопрос")
async def ask(message: types.Message):
    await message.answer("Пожалуйста, напишите свой вопрос в одном сообщении. Мы передадим его в нужный отдел.")

# Обработка пользовательских сообщений
@dp.message_handler()
async def handle_message(message: types.Message):
    text = message.text.lower()

    # Поиск в FAQ
    for question, answer in FAQ.items():
        if question in text:
            await message.answer(answer)
            return

    # Определяем отдел
    if "оплата" in text or "сайт" in text:
        department = "программисты"
    else:
        department = "отдел продаж"

    # Сохраняем в БД
    async with aiosqlite.connect("support.db") as db:
        await db.execute("""
        INSERT INTO requests (user_id, username, message, department)
        VALUES (?, ?, ?, ?)
        """, (message.from_user.id, message.from_user.username, message.text, department))
        await db.commit()

    await message.answer(f"Ваш запрос передан в отдел: {department}. Ожидайте ответа.")

# Запуск
if __name__ == "__main__":
    import asyncio

    async def main():
        await init_db()
        await dp.start_polling()

    asyncio.run(main())