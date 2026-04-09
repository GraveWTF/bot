import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

TOKEN = "8500723553:AAE_PFiZ3eqlP3ep-oormYXiksCfyivkXGw"
ADMIN_ID = 123456789  # вставь свой id

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# 📦 данные
users_cart = {}
user_state = {}
user_data = {}

# 🛍 товары
products = {
    "ALFA VAPE 50MG 30ML": {
        "image": "images/1.jpg",
        "flavors": ["Лесные ягоды", "Клубника банан"]
    },
    "D.L.T.A ENERGY 50MG 30ML": {
        "image": "images/2.jpg",
        "flavors": ["Red bull арбуз", "Monster", "Burn красный", "Adrenaline ягоды", "Adrenaline Rush"]
    },
    "ARQA 100MG": {
        "image": "images/3.jpg",
        "flavors": ["Тропический микс слим", "Ред булл слим", "Кислый грейпфрут", "Арбузная жвачка слим"]
    },
    "ARQA 150MG": {
        "image": "images/4.jpg",
        "flavors": ["Арбуз дыня"]
    },
    "XROS 0.4": {
        "image": "images/5.jpg",
        "flavors": ["Картридж"]
    },
    "XROS 0.6": {
        "image": "images/6.jpg",
        "flavors": ["Картридж"]
    }
}

# 🏠 меню
def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🛍 Товары"))
    kb.add(KeyboardButton("🧺 Корзина"))
    return kb

# ▶️ старт
@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    users_cart[msg.from_user.id] = []
    user_state[msg.from_user.id] = None
    await msg.answer("Добро пожаловать 🔥", reply_markup=main_menu())

# 🛍 показать товары
@dp.message_handler(lambda m: m.text == "🛍 Товары")
async def show_products(msg: types.Message):
    kb = InlineKeyboardMarkup()
    for name in products:
        kb.add(InlineKeyboardButton(name, callback_data=f"prod|{name}"))
    await msg.answer("Выбери товар:", reply_markup=kb)

# 📦 выбор товара
@dp.callback_query_handler(lambda c: c.data.startswith("prod|"))
async def select_product(call: types.CallbackQuery):
    name = call.data.split("|")[1]
    product = products[name]

    kb = InlineKeyboardMarkup()
    for f in product["flavors"]:
        kb.add(InlineKeyboardButton(f, callback_data=f"flavor|{name}|{f}"))

    with open(product["image"], "rb") as photo:
        await bot.send_photo(call.from_user.id, photo, caption=name, reply_markup=kb)

# ➕ добавить в корзину
@dp.callback_query_handler(lambda c: c.data.startswith("flavor|"))
async def add_to_cart(call: types.CallbackQuery):
    _, name, flavor = call.data.split("|")

    users_cart[call.from_user.id].append(f"{name} ({flavor})")

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("➕ Ещё", callback_data="more"))
    kb.add(InlineKeyboardButton("🧺 Корзина", callback_data="cart"))

    await call.message.answer("Добавлено в корзину ✅", reply_markup=kb)

# 🧺 корзина (кнопка)
@dp.message_handler(lambda m: m.text == "🧺 Корзина")
async def cart_message(msg: types.Message):
    await show_cart(msg.from_user.id)

# 🧺 корзина (callback)
@dp.callback_query_handler(lambda c: c.data == "cart")
async def cart_callback(call: types.CallbackQuery):
    await show_cart(call.from_user.id)

# 📋 логика корзины
async def show_cart(user_id):
    cart = users_cart.get(user_id, [])

    if not cart:
        await bot.send_message(user_id, "Корзина пустая ❌")
        return

    text = "🧺 Твоя корзина:\n\n"
    for item in cart:
        text += f"• {item}\n"

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Оформить", callback_data="checkout"))

    await bot.send_message(user_id, text, reply_markup=kb)

# 💳 оформление
@dp.callback_query_handler(lambda c: c.data == "checkout")
async def checkout(call: types.CallbackQuery):
    user_state[call.from_user.id] = "address"
    await call.message.answer("Введи адрес:")

# 📍 адрес
@dp.message_handler(lambda m: user_state.get(m.from_user.id) == "address")
async def get_address(msg: types.Message):
    user_data[msg.from_user.id] = {"address": msg.text}
    user_state[msg.from_user.id] = "phone"
    await msg.answer("Введи номер телефона:")

# 📞 телефон
@dp.message_handler(lambda m: user_state.get(m.from_user.id) == "phone")
async def get_phone(msg: types.Message):
    user_id = msg.from_user.id
    cart = users_cart[user_id]

    address = user_data[user_id]["address"]

    text = "🆕 Заказ\n\n"
    for item in cart:
        text += f"• {item}\n"

    text += f"\n📍 {address}"
    text += f"\n📞 {msg.text}"

    await bot.send_message(ADMIN_ID, text)
    await msg.answer("Заказ оформлен ✅")

    users_cart[user_id] = []
    user_state[user_id] = None

# ▶️ запуск
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
