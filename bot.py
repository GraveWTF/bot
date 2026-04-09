import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

TOKEN = "ТВОЙ_ТОКЕН"
ADMIN_ID = 123456789  # твой id

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

users_cart = {}
user_state = {}

# 📦 Товары
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

# 🏠 Главное меню
def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🛍 Товары"))
    kb.add(KeyboardButton("🧺 Корзина"))
    return kb

# ▶️ Старт
@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    users_cart[msg.from_user.id] = []
    await msg.answer("Добро пожаловать 🔥", reply_markup=main_menu())

# 🛍 Товары
@dp.message_handler(lambda m: m.text == "🛍 Товары")
async def show_products(msg: types.Message):
    kb = InlineKeyboardMarkup()
    for name in products:
        kb.add(InlineKeyboardButton(name, callback_data=f"prod_{name}"))
    await msg.answer("Выбери товар:", reply_markup=kb)

# 📦 Выбор товара
@dp.callback_query_handler(lambda c: c.data.startswith("prod_"))
async def select_product(call: types.CallbackQuery):
    name = call.data.replace("prod_", "")
    product = products[name]

    kb = InlineKeyboardMarkup()
    for f in product["flavors"]:
        kb.add(InlineKeyboardButton(f, callback_data=f"flavor_{name}_{f}"))

    photo = open(product["image"], "rb")
    await bot.send_photo(call.from_user.id, photo, caption=name, reply_markup=kb)

# 🍓 Выбор вкуса → в корзину
@dp.callback_query_handler(lambda c: c.data.startswith("flavor_"))
async def add_to_cart(call: types.CallbackQuery):
    data = call.data.split("_")
    name = data[1]
    flavor = data[2]

    users_cart[call.from_user.id].append(f"{name} ({flavor})")

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("➕ Ещё", callback_data="more"))
    kb.add(InlineKeyboardButton("🧺 Корзина", callback_data="cart"))

    await call.message.answer("Добавлено в корзину ✅", reply_markup=kb)

# 🧺 Показ корзины
@dp.callback_query_handler(lambda c: c.data == "cart")
@dp.message_handler(lambda m: m.text == "🧺 Корзина")
async def show_cart(msg_or_call):
    user_id = msg_or_call.from_user.id
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

# 💳 Оформление
@dp.callback_query_handler(lambda c: c.data == "checkout")
async def checkout(call: types.CallbackQuery):
    user_state[call.from_user.id] = "address"
    await call.message.answer("Введи адрес:")

# 📍 Адрес
@dp.message_handler(lambda m: user_state.get(m.from_user.id) == "address")
async def get_address(msg: types.Message):
    user_state[msg.from_user.id] = "phone"
    msg.bot_data = {"address": msg.text}
    await msg.answer("Введи номер телефона:")

# 📞 Телефон
@dp.message_handler(lambda m: user_state.get(m.from_user.id) == "phone")
async def get_phone(msg: types.Message):
    user_id = msg.from_user.id
    cart = users_cart[user_id]

    text = f"🆕 Заказ\n\n"
    for item in cart:
        text += f"• {item}\n"

    text += f"\n📞 {msg.text}"

    await bot.send_message(ADMIN_ID, text)
    await msg.answer("Заказ оформлен ✅")

    users_cart[user_id] = []
    user_state[user_id] = None

# ▶️ Запуск
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
