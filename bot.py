import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

API_TOKEN = "ТВОЙ_ТОКЕН"
ADMIN_ID = 123456789

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# --- СОСТОЯНИЯ ---
class OrderState(StatesGroup):
    address = State()
    phone = State()

# --- КОРЗИНА ---
user_cart = {}

# --- ТОВАРЫ ---
products = {
    "IZI salt 50mg 30ml": [
        "Гранат смородина",
        "Морс",
        "Черная смородина"
    ],
    "PODONKI PODGON 35mg 30ml": [
        "Дыня банан",
        "Ежевичный лимонад",
        "Земляничная конфета",
        "Кислые червяки",
        "Лесные ягоды",
        "Тропические фрукты"
    ],
    "WAKA 60mg 30ml": [
        "Банан дыня",
        "Вишня арбуз",
        "Ежевичная волна"
    ],
    "Картриджи VAPORESSO XROS 0.4 3ml": [],
    "Картриджи VAPORESSO XROS 0.6 2ml": []
}

# --- СТАРТ ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    text = """HexStore - лучший магазин, с лучшими ценами по всему городу

Доставка:
При заказе от 400 рублей — доставка бесплатная!
При заказе до 400 рублей — доставка 150 рублей.

Время работы:
Северодвинск (12:00 — 21:00)
"""

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🛍 Товары", callback_data="products"))
    kb.add(InlineKeyboardButton("🛒 Корзина", callback_data="cart"))

    with open("banner.png", "rb") as photo:
        await bot.send_photo(message.chat.id, photo, caption=text, reply_markup=kb)

# --- СПИСОК ТОВАРОВ ---
@dp.callback_query_handler(lambda c: c.data == "products")
async def show_products(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup()
    for name in products:
        kb.add(InlineKeyboardButton(name, callback_data=f"product_{name}"))
    await call.message.answer("Выбери товар:", reply_markup=kb)

# --- ВЫБОР ТОВАРА ---
@dp.callback_query_handler(lambda c: c.data.startswith("product_"))
async def choose_product(call: types.CallbackQuery):
    product = call.data.replace("product_", "")
    flavors = products[product]

    if not flavors:
        add_to_cart(call.from_user.id, product)
        await call.message.answer("Добавлено в корзину ✅")
        return

    kb = InlineKeyboardMarkup()
    for f in flavors:
        kb.add(InlineKeyboardButton(f, callback_data=f"add_{product}|{f}"))

    await call.message.answer(f"{product}\nВыбери вкус:", reply_markup=kb)

# --- ДОБАВИТЬ ---
@dp.callback_query_handler(lambda c: c.data.startswith("add_"))
async def add_product(call: types.CallbackQuery):
    data = call.data.replace("add_", "")
    product, flavor = data.split("|")

    add_to_cart(call.from_user.id, f"{product} ({flavor})")

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("➕ Добавить ещё", callback_data="products"))
    kb.add(InlineKeyboardButton("🛒 Корзина", callback_data="cart"))

    await call.message.answer("Добавлено в корзину ✅", reply_markup=kb)

def add_to_cart(user_id, item):
    if user_id not in user_cart:
        user_cart[user_id] = []
    user_cart[user_id].append(item)

# --- КОРЗИНА ---
@dp.callback_query_handler(lambda c: c.data == "cart")
async def show_cart(call: types.CallbackQuery):
    cart = user_cart.get(call.from_user.id, [])

    if not cart:
        await call.message.answer("Корзина пустая ❌")
        return

    text = "🛒 Твоя корзина:\n\n"
    for item in cart:
        text += f"• {item}\n"

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Оформить заказ", callback_data="order"))

    await call.message.answer(text, reply_markup=kb)

# --- ОФОРМЛЕНИЕ ---
@dp.callback_query_handler(lambda c: c.data == "order")
async def order(call: types.CallbackQuery):
    await call.message.answer("Введите адрес:")
    await OrderState.address.set()

@dp.message_handler(state=OrderState.address)
async def get_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("Введите номер телефона:")
    await OrderState.phone.set()

@dp.message_handler(state=OrderState.phone)
async def get_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    address = data['address']
    phone = message.text
    cart = user_cart.get(message.from_user.id, [])

    text = f"""🆕 Новый заказ

📦 Товары:
{chr(10).join(cart)}

📍 Адрес: {address}
📞 Телефон: {phone}
"""

    await bot.send_message(ADMIN_ID, text)
    await message.answer("Заказ оформлен ✅")

    user_cart[message.from_user.id] = []
    await state.finish()

# --- ЗАПУСК ---
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
