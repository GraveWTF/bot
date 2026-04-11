import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

API_TOKEN = "8500723553:AAE_PFiZ3eqlP3ep-oormYXiksCfyivkXGw"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Корзины пользователей
user_cart = {}

# --- ТОВАРЫ ---
products = {
    "IZI salt 50mg 30ml": [
        "гранат смородина",
        "морс",
        "черная смородина"
    ],
    "PODONKI PODGON 35mg 30ml": [
        "дыня банан",
        "ежевичный лимонад",
        "земляничная конфета",
        "кислые червяки",
        "лесные ягоды",
        "тропические фрукты"
    ],
    "WAKA 60mg 30ml": [
        "банан дыня",
        "вишня арбуз",
        "ежевичная волна"
    ],
    "Картриджи VAPORESSO XROS 0.4 3ml": [],
    "Картриджи VAPORESSO XROS 0.6 2ml": []
}

# --- КНОПКИ ---
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(KeyboardButton("🛍 Товары"))
main_kb.add(KeyboardButton("🛒 Корзина"))

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

    # ВСТАВЬ СЮДА СВОЮ КАРТИНКУ В ПАПКУ И НАЗОВИ banner.png
    with open("banner.png", "rb") as photo:
        await bot.send_photo(message.chat.id, photo, caption=text, reply_markup=main_kb)

# --- ТОВАРЫ ---
@dp.message_handler(lambda m: m.text == "🛍 Товары")
async def show_products(message: types.Message):
    kb = InlineKeyboardMarkup()
    for name in products:
        kb.add(InlineKeyboardButton(name, callback_data=f"product_{name}"))
    await message.answer("Выбери товар:", reply_markup=kb)

# --- ВЫБОР ТОВАРА ---
@dp.callback_query_handler(lambda c: c.data.startswith("product_"))
async def choose_product(call: types.CallbackQuery):
    product = call.data.replace("product_", "")

    flavors = products[product]

    if not flavors:
        add_to_cart(call.from_user.id, product)
        await call.message.answer(f"{product} добавлен в корзину ✅")
        return

    kb = InlineKeyboardMarkup()
    for f in flavors:
        kb.add(InlineKeyboardButton(f, callback_data=f"add_{product}|{f}"))

    await call.message.answer(f"{product}\nВыбери вкус:", reply_markup=kb)

# --- ДОБАВИТЬ В КОРЗИНУ ---
@dp.callback_query_handler(lambda c: c.data.startswith("add_"))
async def add_product(call: types.CallbackQuery):
    data = call.data.replace("add_", "")
    product, flavor = data.split("|")

    add_to_cart(call.from_user.id, f"{product} ({flavor})")

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("➕ Добавить ещё", callback_data="more"))
    kb.add(InlineKeyboardButton("🛒 Перейти в корзину", callback_data="cart"))

    await call.message.answer("Добавлено в корзину ✅", reply_markup=kb)

# --- ФУНКЦИЯ КОРЗИНЫ ---
def add_to_cart(user_id, item):
    if user_id not in user_cart:
        user_cart[user_id] = []
    user_cart[user_id].append(item)

# --- ПОКАЗ КОРЗИНЫ ---
@dp.message_handler(lambda m: m.text == "🛒 Корзина")
async def show_cart(message: types.Message):
    cart = user_cart.get(message.from_user.id, [])

    if not cart:
        await message.answer("Корзина пустая ❌")
        return

    text = "🛒 Твоя корзина:\n\n"
    for item in cart:
        text += f"• {item}\n"

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Оформить заказ", callback_data="order"))

    await message.answer(text, reply_markup=kb)

# --- ОФОРМЛЕНИЕ ---
@dp.callback_query_handler(lambda c: c.data == "order")
async def order(call: types.CallbackQuery):
    await call.message.answer("Введите адрес доставки:")
    dp.register_message_handler(get_address, state=None)

async def get_address(message: types.Message):
    user_id = message.from_user.id
    address = message.text

    await message.answer("Введите номер телефона:")
    dp.register_message_handler(lambda m: get_phone(m, address), state=None)

async def get_phone(message: types.Message, address):
    phone = message.text
    cart = user_cart.get(message.from_user.id, [])

    text = f"""🆕 Новый заказ

📦 Товары:
{chr(10).join(cart)}

📍 Адрес: {address}
📞 Телефон: {phone}
"""

    # ВСТАВЬ СВОЙ ID
    ADMIN_ID = 7305195223

    await bot.send_message(ADMIN_ID, text)
    await message.answer("Заказ оформлен ✅")

    user_cart[message.from_user.id] = []

# --- ЗАПУСК ---
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
