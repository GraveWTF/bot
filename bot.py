import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

API_TOKEN = "8500723553:AAE_PFiZ3eqlP3ep-oormYXiksCfyivkXGw"
ADMIN_ID = 7305195223

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

user_cart = {}

# --- FSM ---
class OrderState(StatesGroup):
    address = State()
    phone = State()

# --- ТОВАРЫ ---
products = {
    "IZI salt 50mg 30ml": ["Гранат смородина", "Морс", "Черная смородина"],
    "PODONKI PODGON 35mg 30ml": [
        "Дыня банан", "Ежевичный лимонад", "Земляничная конфета",
        "Кислые червяки", "Лесные ягоды", "Тропические фрукты"
    ],
    "WAKA 60mg 30ml": ["Банан дыня", "Вишня арбуз", "Ежевичная волна"],
    "Картриджи VAPORESSO XROS 0.4 3ml": [],
    "Картриджи VAPORESSO XROS 0.6 2ml": []
}

# --- СТАРТ ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🛍 Товары", callback_data="products"))
    kb.add(InlineKeyboardButton("🛒 Корзина", callback_data="cart"))

    await message.answer("Добро пожаловать в HexStore 🔥", reply_markup=kb)

# --- СПИСОК ТОВАРОВ ---
@dp.callback_query_handler(lambda c: c.data == "products")
async def products_menu(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup()
    for p in products:
        kb.add(InlineKeyboardButton(p, callback_data=f"product:{p}"))

    await call.message.edit_text("Выбери товар:", reply_markup=kb)

# --- ВЫБОР ТОВАРА ---
@dp.callback_query_handler(lambda c: c.data.startswith("product:"))
async def product(call: types.CallbackQuery):
    name = call.data.split(":")[1]
    flavors = products[name]

    if not flavors:
        add_to_cart(call.from_user.id, name)
        await call.answer("Добавлено ✅", show_alert=False)
        return

    kb = InlineKeyboardMarkup()
    for f in flavors:
        kb.add(InlineKeyboardButton(f, callback_data=f"add:{name}|{f}"))

    await call.message.edit_text(f"{name}\nВыбери вкус:", reply_markup=kb)

# --- ДОБАВИТЬ ---
@dp.callback_query_handler(lambda c: c.data.startswith("add:"))
async def add(call: types.CallbackQuery):
    data = call.data.split(":")[1]
    name, flavor = data.split("|")

    add_to_cart(call.from_user.id, f"{name} ({flavor})")

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("➕ Добавить ещё", callback_data="products"))
    kb.add(InlineKeyboardButton("🛒 Корзина", callback_data="cart"))

    await call.message.edit_text("Добавлено в корзину ✅", reply_markup=kb)

def add_to_cart(user_id, item):
    user_cart.setdefault(user_id, []).append(item)

# --- КОРЗИНА ---
@dp.callback_query_handler(lambda c: c.data == "cart")
async def cart(call: types.CallbackQuery):
    cart = user_cart.get(call.from_user.id, [])

    if not cart:
        await call.answer("Корзина пустая ❌", show_alert=True)
        return

    text = "🛒 Корзина:\n\n" + "\n".join(f"• {i}" for i in cart)

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Оформить заказ", callback_data="order"))

    await call.message.edit_text(text, reply_markup=kb)

# --- ОФОРМЛЕНИЕ ---
@dp.callback_query_handler(lambda c: c.data == "order")
async def order(call: types.CallbackQuery):
    await call.message.answer("Введите адрес:")
    await OrderState.address.set()

@dp.message_handler(state=OrderState.address)
async def address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("Введите телефон:")
    await OrderState.phone.set()

@dp.message_handler(state=OrderState.phone)
async def phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cart = user_cart.get(message.from_user.id, [])

    text = f"""🆕 Заказ

{chr(10).join(cart)}

Адрес: {data['address']}
Телефон: {message.text}
"""

    await bot.send_message(ADMIN_ID, text)
    await message.answer("Заказ оформлен ✅")

    user_cart[message.from_user.id] = []
    await state.finish()

# --- ЗАПУСК ---
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
