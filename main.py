import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# Конфигурация
BOT_TOKEN = "7604459732:AAE49WdblJZh_GyspEfJetWLm-PZUv1vRBI"  # Замените на токен от @BotFather
CHANNEL_ID = "@tgksample"     # Замените на username канала (например: "@my_test_channel")

# Инициализация объектов
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

HARDCODED_TEXT = "https://www.twitch.tv/zombyaak_doto"
HARDCODED_PHOTO_URL = "https://i.pinimg.com/736x/10/64/17/1064170e45d615504439a05be4d88c5c.jpg"  # Замените на реальную ссылку
CUSTOM_TEXT = "🚀 Пользовательский текст с фото!"

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Состояния FSM
class Form(StatesGroup):
    waiting_for_text = State()
    waiting_for_photo = State()

# Главное меню с 3 кнопками
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📸 Хардкод текст + стандартное фото")],
        [KeyboardButton(text="✏️ Пользовательский текст + стандартное фото")],
        [KeyboardButton(text="🖼️ Хардкод текст + своё фото")],
        [KeyboardButton(text="❌ Отменить")]
    ],
    resize_keyboard=True
)

# Обработчик /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "Выберите тип отправки:",
        reply_markup=main_keyboard
    )


@dp.message(lambda message: message.text == "Дефолт сообщение")
async def send_hardcoded_with_photo(message: types.Message):
    try:
        # Отправляем фото с подписью в канал
        await bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=HARDCODED_PHOTO_URL,
            caption=HARDCODED_TEXT
        )
        await message.answer("✅ Сообщение отправлено: стандартный текст + фото!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")

# Кнопка 2: Пользовательский текст + стандартное фото
@dp.message(lambda message: message.text == "✏️ Пользовательский текст + стандартное фото")
async def request_custom_text(message: types.Message, state: FSMContext):
    await message.answer(
        "Введите текст сообщения:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Form.waiting_for_text)

# Обработчик текста для кнопки 2
@dp.message(Form.waiting_for_text)
async def send_custom_text_with_photo(message: types.Message, state: FSMContext):
    try:
        # Отправляем стандартное фото с пользовательским текстом
        await bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=HARDCODED_PHOTO_URL,
            caption=f"{message.text}\n\nОтправитель: {message.from_user.full_name}"
        )
        await message.answer(
            "✅ Сообщение отправлено: ваш текст + стандартное фото!",
            reply_markup=main_keyboard
        )
    except Exception as e:
        await message.answer(
            f"❌ Ошибка: {str(e)}",
            reply_markup=main_keyboard
        )
    finally:
        await state.clear()

# Кнопка 3: Хардкод текст + своё фото
@dp.message(lambda message: message.text == "🖼️ Хардкод текст + своё фото")
async def request_custom_photo(message: types.Message, state: FSMContext):
    await message.answer(
        "Отправьте фото:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Form.waiting_for_photo)

# Обработчик фото для кнопки 3
@dp.message(Form.waiting_for_photo)
async def send_hardcoded_text_with_photo(message: types.Message, state: FSMContext):
    try:
        # Проверяем, что сообщение содержит фото
        if message.photo:
            # Берем последнее (самое высокое качество) фото
            photo_file_id = message.photo[-1].file_id
            
            # Отправляем пользовательское фото с хардкодным текстом
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=photo_file_id,
                caption=CUSTOM_TEXT
            )
            await message.answer(
                "✅ Сообщение отправлено: хардкодный текст + ваше фото!",
                reply_markup=main_keyboard
            )
        else:
            await message.answer(
                "❌ Вы отправили не фото. Попробуйте еще раз.",
                reply_markup=main_keyboard
            )
    except Exception as e:
        await message.answer(
            f"❌ Ошибка: {str(e)}",
            reply_markup=main_keyboard
        )
    finally:
        await state.clear()

# Обработчик отмены
@dp.message(lambda message: message.text == "❌ Отменить")
async def cancel_action(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    await message.answer(
        "Действие отменено",
        reply_markup=main_keyboard
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())