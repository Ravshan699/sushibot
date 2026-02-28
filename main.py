import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
    LabeledPrice,
    PreCheckoutQuery
)
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode

API_TOKEN = "YOUR_BOT_TOKEN"
ADMIN_ID = 123456789
PAYMENT_PROVIDER_TOKEN = "YOUR_PAYMENT_PROVIDER_TOKEN"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(
            text="🍣 Меню",
            web_app=WebAppInfo(url="https://YOUR_RENDER_URL.onrender.com")
        )]
    ],
    resize_keyboard=True
)

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🍣 <b>Суши Катана Самарканд</b>\n\nВыберите меню 👇",
        reply_markup=menu_keyboard
    )

# Получаем данные из Mini App
@dp.message(F.web_app_data)
async def webapp_handler(message: Message):
    order_data = message.web_app_data.data
    
    await message.answer("📍 Введите адрес доставки:")
    
    dp["order"] = order_data
    dp["user_id"] = message.from_user.id

# Получаем адрес
@dp.message()
async def get_address(message: Message):
    order = dp.get("order")
    
    if not order:
        return
    
    address = message.text
    
    prices = [LabeledPrice(label="Заказ Суши Катана", amount=10000)]
    
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Оплата заказа 🍣",
        description="Оплата суши",
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency="UZS",
        prices=prices,
        payload="sushi-payment"
    )
    
    dp["address"] = address

# Подтверждение оплаты
@dp.pre_checkout_query()
async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def successful_payment(message: Message):
    order = dp.get("order")
    address = dp.get("address")
    
    text = f"""
🔥 <b>Новый оплаченный заказ!</b>

👤 {message.from_user.full_name}
📍 {address}

🛒 {order}
"""
    
    await bot.send_message(ADMIN_ID, text)
    await message.answer("✅ Оплата прошла успешно! Заказ принят.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())