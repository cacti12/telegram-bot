import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from openpyxl import load_workbook

# 🔐 токен из Render
API_TOKEN = os.getenv("BOT_TOKEN")

if not API_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден! Добавь его в Render")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- СТАТУСЫ ---
STAGES = {
    1: "🛒 Заказ оформлен",
    2: "🇺🇸 На складе в США",
    3: "🇪🇺 Транзитный рейс в Европе",
    4: "🇷🇺 Таможня в Москве",
    5: "✅ Доставлен в РФ"
}

# --- ПОИСК ЗАКАЗА ---
def find_order(order_id):
    wb = load_workbook("orders1.xlsx")
    ws = wb.active

    for row in ws.iter_rows(min_row=2, values_only=True):
        if str(row[0]) == str(order_id):
            return {
                "order_id": row[0],
                "status": row[3]
            }
    return None

# --- СТАРТ ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📦 Отследить заказ")
    await message.answer("Выберите действие:", reply_markup=kb)

# --- КНОПКА ---
@dp.message_handler(lambda m: m.text == "📦 Отследить заказ")
async def track(message: types.Message):
    await message.answer("Введите номер заказа:")

# --- ОБРАБОТКА ---
@dp.message_handler()
async def handle(message: types.Message):
    order_id = message.text.strip()
    order = find_order(order_id)

    if not order:
        await message.answer("❌ Заказ не найден")
        return

    stage = int(order["status"])
    current_status = STAGES.get(stage, "Неизвестный статус")

    text = f"""
📦 Заказ: {order['order_id']}

📍 Статус:
{current_status}
"""

    await message.answer(text)

# --- ЗАПУСК (ОЧЕНЬ ВАЖНО) ---
if __name__ == "__main__":
    import asyncio

    async def on_startup(dp):
        # 🔥 убираем конфликт Telegram
        await bot.delete_webhook(drop_pending_updates=True)

    print("🚀 БОТ ЗАПУЩЕН")
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

