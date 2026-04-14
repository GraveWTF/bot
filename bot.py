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
user_state = {}

# 📦 товары
products = {
    "1": ("IZI salt 50mg 30ml | 250₽",
          ["Гранат смородина", "Морс", "Черная смородина"]),
    "2": ("PODONKI PODGON 35mg 30ml | 350₽",
          ["Дыня банан", "Ежевичный лимонад", "Земляничная конфета",
           "Кислые червяки", "Лесные ягоды", "Тропические фрукты"]),
    "3": ("WAKA 60mg 30ml | 350₽",
          ["Банан дыня", "Вишня арбуз", "Ежевичная волна"]),
    "4": ("Картриджи VAPORESSO XROS 0.4 3ml | 300₽", ["Без вкуса"]),
    "5": ("Картриджи VAPORESSO XROS 0.6 2ml | 300₽", ["Без вкуса"])
}

# 🔥 главное меню
def main_menu():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📦 Товар", callback_data="products"),
        InlineKeyboardButton("🛒 Корзина", callback_data="cart"),
        InlineKeyboardButton("📞 Поддержка", callback_data="support")
    )
    return kb

# 📦 список товаров
def products_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    for key, val in products.items():
        kb.add(InlineKeyboardButton(val[0], callback_data=f"product_{key}"))
    kb.add(InlineKeyboardButton("⬅ Назад", callback_data="menu"))
    return kb

# 🍓 вкусы
def flavors_kb(key):
    kb = InlineKeyboardMarkup(row_width=1)
    for f in products[key][1]:
        kb.add(InlineKeyboardButton(f, callback_data=f"flavor_{key}_{f}"))
    kb.add(InlineKeyboardButton("⬅ Назад", callback_data="products"))
    return kb

# 🚀 старт
@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    text = (
        "HexStore - лучший магазин, с лучшими ценами по всему городу\n\n"
        "Время работы:\n"
        "Северодвинск ( 12:00 — 21:00)"
    )
    await msg.answer(text, reply_markup=main_menu())

# 🔙 меню
@dp.callback_query_handler(lambda c: c.data == "menu")
async def menu(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text("Главное меню:", reply_markup=main_menu())

# 📦 открыть товары
@dp.callback_query_handler(lambda c: c.data == "products")
async def show_products(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text(
        "Выберите товар который вы хотите приобрести",
        reply_markup=products_kb()
    )

# 📞 поддержка
@dp.callback_query_handler(lambda c: c.data == "support")
async def support(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer(
        "📞 Поддержка:\n@HexStoreManager\n@Hex_Store_Manager"
    )

# 📦 выбор товара
@dp.callback_query_handler(lambda c: c.data.startswith("product_"))
async def product(call: types.CallbackQuery):
    await call.answer()
    key = call.data.split("_")[1]

    await call.message.edit_text(
        "Выберите ваш вкус",
        reply_markup=flavors_kb(key)
    )

# 🍓 добавление в корзину
@dp.callback_query_handler(lambda c: c.data.startswith("flavor_"))
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

    await call.message.edit_text("✅ Товар добавлен в корзину", reply_markup=kb)

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
        InlineKeyboardButton("⬅ Назад", callback_data="menu")
    )

    await call.message.edit_text(text, reply_markup=kb)

# ✅ оформление
@dp.callback_query_handler(lambda c: c.data == "checkout")
async def checkout(call: types.CallbackQuery):
    await call.answer()
    user_state[call.from_user.id] = "phone"
    await call.message.answer("Введите ваш номер:")

# 📱 ввод номера
@dp.message_handler(lambda m: user_state.get(m.from_user.id) == "phone")
async def get_phone(msg: types.Message):
    user_state[msg.from_user.id] = "address"
    user_cart[msg.from_user.id].append(f"📱 Телефон: {msg.text}")
    await msg.answer("Введите ваш адрес:")

# 🏠 ввод адреса
@dp.message_handler(lambda m: user_state.get(m.from_user.id) == "address")
async def get_address(msg: types.Message):
    uid = msg.from_user.id
    user_cart[uid].append(f"🏠 Адрес: {msg.text}")

    order = "🛒 Новый заказ:\n\n"
    for item in user_cart[uid]:
        order += f"{item}\n"

    order += f"\n👤 @{msg.from_user.username or uid}"

    await bot.send_message("@HexStoreManager", order)

    await msg.answer(
        "✅ Заказ отправлен!\nНапишите менеджеру:",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Перейти к менеджеру", url="https://t.me/HexStoreManager")
        )
    )

    user_cart[uid] = []
    user_state[uid] = None

# ▶️ запуск
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
