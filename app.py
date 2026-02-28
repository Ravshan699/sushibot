import os
import asyncio
import json
from flask import Flask, render_template, redirect, request
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
    WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import CommandStart
from database import SessionLocal, Order, init_db
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

app = Flask(__name__)
init_db()

user_data = {}

# ---------- TELEGRAM BOT ----------

menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(
        text="🍣 Меню",
        web_app=WebAppInfo(url=os.getenv("WEBAPP_URL"))
    )]],
    resize_keyboard=True
)

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🍣 Sushi Katana Самарканд\n\nВыберите меню 👇",
        reply_markup=menu_keyboard
    )

@dp.message(F.web_app_data)
async def get_order(message: Message):
    data = json.loads(message.web_app_data.data)
    user_data[message.from_user.id] = data
    await message.answer("📞 Введите номер телефона:")

@dp.message()
async def handle_user_data(message: Message):
    uid = message.from_user.id
    if uid not in user_data:
        return
    
    data = user_data[uid]
    
    if "phone" not in data:
        data["phone"] = message.text
        await message.answer("📍 Введите адрес доставки:")
        return
    
    if "address" not in data:
        data["address"] = message.text
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Онлайн", callback_data="online")],
            [InlineKeyboardButton(text="💵 Наличными", callback_data="cash")]
        ])
        
        await message.answer("Выберите способ оплаты:", reply_markup=keyboard)
        return

@dp.callback_query()
async def payment(callback):
    uid = callback.from_user.id
    data = user_data[uid]
    data["payment_type"] = callback.data

    db = SessionLocal()
    order = Order(
        name=callback.from_user.full_name,
        phone=data["phone"],
        address=data["address"],
        items=", ".join(data["order"]),
        total=data["total"],
        payment_type=data["payment_type"]
    )
    db.add(order)
    db.commit()
    db.close()

    await callback.message.answer("✅ Заказ принят!")
    await callback.answer()

# ---------- ADMIN PANEL ----------

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == ADMIN_PASSWORD:
            return redirect("/dashboard")
    return """
    <form method="post">
    <input type="password" name="password" placeholder="Пароль">
    <button type="submit">Войти</button>
    </form>
    """

@app.route("/dashboard")
def dashboard():
    db = SessionLocal()
    orders = db.query(Order).order_by(Order.id.desc()).all()
    db.close()
    return render_template("dashboard.html", orders=orders)

@app.route("/status/<int:order_id>/<string:new_status>")
def change_status(order_id, new_status):
    db = SessionLocal()
    order = db.query(Order).filter(Order.id == order_id).first()
    order.status = new_status
    db.commit()
    db.close()
    return redirect("/dashboard")

@app.route("/stats")
def stats():
    db = SessionLocal()
    orders = db.query(Order).all()
    today = sum(o.total for o in orders)
    count = len(orders)
    db.close()
    return f"Заказов: {count} | Общая сумма: {today} сум"

# ---------- RUN ----------

async def start_bot():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: asyncio.run(start_bot())).start()
    app.run(host="0.0.0.0", port=10000)