import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

API_TOKEN = "8500723553:AAE_PFiZ3eqlP3ep-oormYXiksCfyivkXGw"
ADMIN_ID = 7305195223

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_cart = {}

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

    await message.answer("HexStore 🔥", reply_markup=kb)

# --- ТОВАРЫ ---
@dp.callback_query_handler(lambda c: c.data == "products")
async def products_menu(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup()
    for p in products:
        kb.add(InlineKeyboardButton(p, callback_data=f"product|{p}"))

    await call.message.answer("Выбери товар:", reply_markup=kb)

# --- ВЫБОР ---
@dp.callback_query_handler(lambda c: c.data.startswith("product|"))
async def product(call: types.CallbackQuery):
    name = call.data.split("|")[1]
    flavors = products[name]

    if not flavors:
        add_to_cart(call.from_user.id, name)
        await call.answer("Добавлено в корзину ✅")
        return

    kb = InlineKeyboardMarkup()
    for f in flavors:
        kb.add(InlineKeyboardButton(f, callback_data=f"add|{name}|{f}"))

    await call.message.answer(f"{name}\nВыбери вкус:", reply_markup=kb)

# --- ДОБАВИТЬ ---
@dp.callback_query_handler(lambda c: c.data.startswith("add|"))
async def add(call: types.CallbackQuery):
    _, name, flavor = call.data.split("|")

    add_to_cart(call.from_user.id, f"{name} ({flavor})")

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("➕ Добавить ещё", callback_data="products"))
    kb.add(InlineKeyboardButton("🛒 Корзина", callback_data="cart"))

    await call.message.answer("Добавлено в корзину ✅", reply_markup=kb)

def add_to_cart(user_id, item):
    user_cart.setdefault(user_id, []).append(item)
    print(user_cart)  # ДЛЯ ПРОВЕРКИ В ЛОГАХ

# --- КОРЗИНА ---
@dp.callback_query_handler(lambda c: c.data == "cart")
async def cart(call: types.CallbackQuery):
    cart = user_cart.get(call.from_user.id, [])

    if not cart:
        await call.message.answer("Корзина пустая ❌")
        return

    text = "🛒 Корзина:\n\n" + "\n".join(f"• {i}" for i in cart)

    await call.message.answer(text)

# --- ЗАПУСК ---
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
