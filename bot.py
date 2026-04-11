import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

API_TOKEN = "8500723553:AAE_PFiZ3eqlP3ep-oormYXiksCfyivkXGw"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# 🛒 корзина
user_cart = {}

# 📦 товары
products = {
    "izi": ("IZI salt 50mg 30ml", ["Гранат смородина", "Морс", "Черная смородина"]),
    "podonki": ("PODONKI PODGON 35mg 30ml", [
        "Дыня банан", "Ежевичный лимонад", "Земляничная конфета",
        "Кислые червяки", "Лесные ягоды", "Тропические фрукты"
    ]),
    "waka": ("WAKA 60mg 30ml", ["Банан дыня", "Вишня арбуз", "Ежевичная волна"]),
    "xros04": ("Картриджи VAPORESSO XROS 0.4 3ml", ["Без вкуса"]),
    "xros06": ("Картриджи VAPORESSO XROS 0.6 2ml", ["Без вкуса"])
}

# 🔥 ГЛАВНОЕ МЕНЮ
def main_menu():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📦 Товары", callback_data="products"),
        InlineKeyboardButton("🛒 Корзина", callback_data="cart"),
        InlineKeyboardButton("📞 Поддержка", url="https://t.me/HexStoreManager")
    )
    return kb

# 📦 список товаров
def products_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    for key in products:
        kb.add(InlineKeyboardButton(products[key][0], callback_data=f"p_{key}"))
    kb.add(InlineKeyboardButton("⬅ Назад", callback_data="back"))
    return kb

# 🍓 вкусы
def flavors_kb(key):
    kb = InlineKeyboardMarkup(row_width=1)
    for f in products[key][1]:
        kb.add(InlineKeyboardButton(f, callback_data=f"f_{key}_{f}"))
    kb.add(InlineKeyboardButton("⬅ Назад", callback_data="products"))
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

    await msg.answer(text, reply_markup=main_menu())

# 📦 открыть товары
@dp.callback_query_handler(lambda c: c.data == "products")
async def show_products(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text("Выбери товар:", reply_markup=products_kb())

# 🔙 назад
@dp.callback_query_handler(lambda c: c.data == "back")
async def back(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text("Меню:", reply_markup=main_menu())

# 📦 выбор товара
@dp.callback_query_handler(lambda c: c.data.startswith("p_"))
async def product(call: types.CallbackQuery):
    await call.answer()
    key = call.data.split("_")[1]
    await call.message.edit_text(
        f"Выбери вкус для {products[key][0]}:",
        reply_markup=flavors_kb(key)
    )

# 🍓 добавление в корзину
@dp.callback_query_handler(lambda c: c.data.startswith("f_"))
async def add_to_cart(call: types.CallbackQuery):
    await call.answer()

    _, key, flavor = call.data.split("_", 2)
    user_id = call.from_user.id

    item = f"{products[key][0]} - {flavor}"

    if user_id not in user_cart:
        user_cart[user_id] = []

    user_cart[user_id].append(item)

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("➕ Добавить ещё", callback_data="products"),
        InlineKeyboardButton("🛒 Корзина", callback_data="cart")
    )

    await call.message.edit_text("✅ Добавлено в корзину", reply_markup=kb)

# 🛒 корзина
@dp.callback_query_handler(lambda c: c.data == "cart")
async def cart(call: types.CallbackQuery):
    await call.answer()
    uid = call.from_user.id

    if uid not in user_cart or not user_cart[uid]:
        await call.message.edit_text("🛒 Корзина пустая", reply_markup=main_menu())
        return

    text = "🛒 Ваша корзина:\n\n"
    for item in user_cart[uid]:
        text += f"• {item}\n"

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("✅ Оформить заказ", callback_data="checkout"),
        InlineKeyboardButton("⬅ Назад", callback_data="back")
    )

    await call.message.edit_text(text, reply_markup=kb)

# ✅ оформление
@dp.callback_query_handler(lambda c: c.data == "checkout")
async def checkout(call: types.CallbackQuery):
    await call.answer()

    uid = call.from_user.id

    if uid not in user_cart:
        return

    order = "🛒 Новый заказ:\n\n"
    for i in user_cart[uid]:
        order += f"• {i}\n"

    order += f"\n👤 @{call.from_user.username or uid}"

    await bot.send_message("@HexStoreManager", order)

    await call.message.edit_text("✅ Заказ отправлен!", reply_markup=main_menu())

    user_cart[uid] = []

# ▶️ запуск
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
