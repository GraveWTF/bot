import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.utils import executor

API_TOKEN = "8500723553:AAE_PFiZ3eqlP3ep-oormYXiksCfyivkXGw"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_cart = {}

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

# 📦 товары
def products_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    for key in products:
        kb.add(InlineKeyboardButton(products[key]["name"], callback_data=f"product_{key}"))
    return kb

# 🍓 вкусы
def flavors_kb(key):
    kb = InlineKeyboardMarkup(row_width=1)
    for f in products[key]["flavors"]:
        kb.add(InlineKeyboardButton(f, callback_data=f"flavor_{key}_{f}"))
    return kb

# 🚀 старт
@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    text = (
        "HexStore - лучший магазин, с лучшими ценами по всему городу\n\n"
        "Доставка:\n"
        "При заказе от 400 рублей — доставка бесплатная!\n"
        "При заказе до 400 рублей — доставка 150 рублей.\n\n"
        "Время работы:\n"
        "Северодвинск (12:00 — 21:00)"
    )

    # 🔥 КАРТИНКА (положи файл banner.jpg рядом с bot.py)
    photo = InputFile("banner.jpg")

    await msg.answer_photo(photo, caption=text)
    await msg.answer("Выбери товар:", reply_markup=products_kb())

# 📦 выбор товара
@dp.callback_query_handler(lambda c: c.data.startswith("product_"))
async def product(call: types.CallbackQuery):
    await call.answer()

    key = call.data.split("_")[1]

    await call.message.answer(
        f"Выбери вкус для {products[key]['name']}:",
        reply_markup=flavors_kb(key)
    )

# 🍓 выбор вкуса
@dp.callback_query_handler(lambda c: c.data.startswith("flavor_"))
async def flavor(call: types.CallbackQuery):
    await call.answer()

    _, key, flavor = call.data.split("_", 2)

    user_id = call.from_user.id

    item = f"{products[key]['name']} - {flavor}"

    if user_id not in user_cart:
        user_cart[user_id] = []

    user_cart[user_id].append(item)

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("➕ Добавить ещё", callback_data="more"))
    kb.add(InlineKeyboardButton("🛒 Корзина", callback_data="cart"))

    await call.message.answer("✅ Добавлено!", reply_markup=kb)

# ➕ добавить еще
@dp.callback_query_handler(lambda c: c.data == "more")
async def more(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer("Выбери товар:", reply_markup=products_kb())

# 🛒 корзина
@dp.callback_query_handler(lambda c: c.data == "cart")
async def cart(call: types.CallbackQuery):
    await call.answer()

    uid = call.from_user.id

    if uid not in user_cart or not user_cart[uid]:
        await call.message.answer("🛒 Корзина пустая")
        return

    text = "🛒 Ваша корзина:\n\n"
    for item in user_cart[uid]:
        text += f"• {item}\n"

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Оформить", callback_data="checkout"))

    await call.message.answer(text, reply_markup=kb)

# ✅ оформление
@dp.callback_query_handler(lambda c: c.data == "checkout")
async def checkout(call: types.CallbackQuery):
    await call.answer()

    uid = call.from_user.id

    if uid not in user_cart or not user_cart[uid]:
        await call.message.answer("Корзина пустая")
        return

    order = "🛒 Новый заказ:\n\n"
    for i in user_cart[uid]:
        order += f"• {i}\n"

    order += f"\n👤 @{call.from_user.username or uid}"

    await bot.send_message("@HexStoreManager", order)

    await call.message.answer("✅ Заказ отправлен!")

    user_cart[uid] = []

# ▶️ запуск
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
