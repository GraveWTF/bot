import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

API_TOKEN = "8500723553:AAE_PFiZ3eqlP3ep-oormYXiksCfyivkXGw"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# 🛒 Хранилище
user_cart = {}
current_product = {}

# 📦 Товары
products = {
    "izi": {
        "name": "IZI salt 50mg 30ml",
        "flavors": ["Гранат смородина", "Морс", "Черная смородина"]
    },
    "podonki": {
        "name": "PODONKI PODGON 35mg 30ml",
        "flavors": [
            "Дыня банан",
            "Ежевичный лимонад",
            "Земляничная конфета",
            "Кислые червяки",
            "Лесные ягоды",
            "Тропические фрукты"
        ]
    },
    "waka": {
        "name": "WAKA 60mg 30ml",
        "flavors": [
            "Банан дыня",
            "Вишня арбуз",
            "Ежевичная волна"
        ]
    },
    "xros04": {
        "name": "Картриджи VAPORESSO XROS 0.4 3ml",
        "flavors": ["Без вкуса"]
    },
    "xros06": {
        "name": "Картриджи VAPORESSO XROS 0.6 2ml",
        "flavors": ["Без вкуса"]
    }
}

# 📋 Клавиатура товаров
def get_products_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    for key, item in products.items():
        kb.add(InlineKeyboardButton(item["name"], callback_data=f"product_{key}"))
    return kb

# 📋 Клавиатура вкусов
def get_flavors_kb(product_key):
    kb = InlineKeyboardMarkup(row_width=1)
    for flavor in products[product_key]["flavors"]:
        kb.add(InlineKeyboardButton(flavor, callback_data=f"flavor_{product_key}_{flavor}"))
    return kb

# 🚀 Старт
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    text = (
        "HexStore - лучший магазин, с лучшими ценами по всему городу\n\n"
        "Доставка:\n"
        "При заказе от 400 рублей — доставка бесплатная!\n"
        "При заказе до 400 рублей — доставка 150 рублей.\n\n"
        "Время работы:\n"
        "Северодвинск (12:00 — 21:00)"
    )

    await message.answer(text)
    await message.answer("Выбери товар:", reply_markup=get_products_kb())

# 📦 Выбор товара
@dp.callback_query_handler(lambda c: c.data.startswith("product_"))
async def choose_product(call: types.CallbackQuery):
    user_id = call.from_user.id
    product_key = call.data.split("_")[1]

    current_product[user_id] = product_key

    await call.message.answer(
        f"Выберите вкус для {products[product_key]['name']}:",
        reply_markup=get_flavors_kb(product_key)
    )

# 🍓 Выбор вкуса и добавление в корзину
@dp.callback_query_handler(lambda c: c.data.startswith("flavor_"))
async def choose_flavor(call: types.CallbackQuery):
    user_id = call.from_user.id

    _, product_key, flavor = call.data.split("_", 2)

    item = f"{products[product_key]['name']} - {flavor}"

    if user_id not in user_cart:
        user_cart[user_id] = []

    user_cart[user_id].append(item)

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("➕ Добавить ещё", callback_data="add_more"))
    kb.add(InlineKeyboardButton("🛒 Корзина", callback_data="cart"))

    await call.message.answer("Добавлено в корзину ✅", reply_markup=kb)

# ➕ Добавить ещё
@dp.callback_query_handler(lambda c: c.data == "add_more")
async def add_more(call: types.CallbackQuery):
    await call.message.answer("Выбери товар:", reply_markup=get_products_kb())

# 🛒 Корзина
@dp.callback_query_handler(lambda c: c.data == "cart")
async def show_cart(call: types.CallbackQuery):
    user_id = call.from_user.id

    if user_id not in user_cart or not user_cart[user_id]:
        await call.message.answer("🛒 Корзина пустая")
        return

    text = "🛒 Ваша корзина:\n\n"
    for item in user_cart[user_id]:
        text += f"• {item}\n"

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Оформить заказ", callback_data="checkout"))

    await call.message.answer(text, reply_markup=kb)

# ✅ Оформление заказа
@dp.callback_query_handler(lambda c: c.data == "checkout")
async def checkout(call: types.CallbackQuery):
    user_id = call.from_user.id

    if user_id not in user_cart or not user_cart[user_id]:
        await call.message.answer("Корзина пустая")
        return

    order_text = "🛒 Новый заказ:\n\n"
    for item in user_cart[user_id]:
        order_text += f"• {item}\n"

    order_text += f"\n👤 @{call.from_user.username or call.from_user.id}"

    # отправка менеджеру
    await bot.send_message("@HexStoreManager", order_text)

    await call.message.answer("✅ Заказ отправлен!")

    user_cart[user_id] = []

# ▶️ Запуск
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
