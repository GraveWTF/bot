import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

TOKEN = "8500723553:AAE_PFiZ3eqlP3ep-oormYXiksCfyivkXGw"

from aiogram.client.session.aiohttp import AiohttpSession

bot = Bot(token=TOKEN)
dp = Dispatcher()


# ---------- FSM ----------
class OrderState(StatesGroup):
    choosing_flavor = State()
    waiting_address = State()
    waiting_phone = State()


# ---------- Клавиатуры ----------
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛍 Товар")],
        [KeyboardButton(text="🛒 Корзина")],
        [KeyboardButton(text="📞 Поддержка")]
    ],
    resize_keyboard=True
)

flavors_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Черная смородина", callback_data="flavor_смородина")],
        [InlineKeyboardButton(text="Морс", callback_data="flavor_морс")],
        [InlineKeyboardButton(text="Грейпфрут", callback_data="flavor_грейпфрут")],
        [InlineKeyboardButton(text="Гранат смородина", callback_data="flavor_гранат")],
        [InlineKeyboardButton(text="Ананас", callback_data="flavor_ананас")],
        [InlineKeyboardButton(text="Банан", callback_data="flavor_банан")]
    ]
)


# ---------- Старт ----------
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Добро пожаловать в магазин!", reply_markup=main_kb)


# ---------- Раздел товар ----------
@dp.message(F.text == "🛍 Товар")
async def show_product(message: Message, state: FSMContext):
    photo = FSInputFile("image.png")  # файл картинки рядом с ботом

    await message.answer_photo(
        photo=photo,
        caption="📦 IZI salt 50mg 30 ml\n\nВыберите вкус:",
        reply_markup=flavors_kb
    )
    await state.set_state(OrderState.choosing_flavor)


# ---------- Выбор вкуса ----------
@dp.callback_query(F.data.startswith("flavor_"))
async def choose_flavor(callback, state: FSMContext):
    flavor = callback.data.split("_")[1]

    await state.update_data(flavor=flavor)

    await callback.message.answer("📍 Введите ваш адрес:")
    await state.set_state(OrderState.waiting_address)


# ---------- Адрес ----------
@dp.message(OrderState.waiting_address)
async def get_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)

    await message.answer("📞 Введите номер телефона:")
    await state.set_state(OrderState.waiting_phone)


# ---------- Телефон ----------
@dp.message(OrderState.waiting_phone)
async def get_phone(message: Message, state: FSMContext):
    data = await state.get_data()

    flavor = data["flavor"]
    address = data["address"]
    phone = message.text

    text = (
        f"🛒 Заказ:\n"
        f"Товар: IZI salt 50mg 30 ml\n"
        f"Вкус: {flavor}\n"
        f"Адрес: {address}\n"
        f"Телефон: {phone}"
    )

    manager_link = f"https://t.me/HexStoreManager?text={text}"

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📩 Связаться с менеджером", url=manager_link)]
        ]
    )

    await message.answer("Нажмите кнопку ниже для оформления заказа:", reply_markup=kb)

    await state.clear()


# ---------- Поддержка ----------
@dp.message(F.text == "📞 Поддержка")
async def support(message: Message):
    await message.answer("Связь с поддержкой: @HexStoreManager")


# ---------- Корзина ----------
@dp.message(F.text == "🛒 Корзина")
async def cart(message: Message):
    await message.answer("🛒 Корзина пока пустая")


# ---------- Запуск ----------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
