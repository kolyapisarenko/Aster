import asyncio
import logging
from datetime import date
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardButton, WebAppInfo
import requests
import os
import time
from utils.database import (
    get_habits_for_today, log_habit, get_current_balance, 
    feed_piggy_bank
)

def get_ngrok_url():
    time.sleep(5) 
    try:
        response = requests.get("http://ngrok-tunnel:4040/api/tunnels")
        data = response.json()
        return data['tunnels'][0]['public_url']
    except Exception as e:
        print(f"Error getting ngrok URL: {e}")
        return "http://localhost:8502" 
    
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEB_APP_URL = get_ngrok_url()

if not TOKEN:
    raise ValueError("No TELEGRAM_BOT_TOKEN found in environment variables!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

class HabitStates(StatesGroup):
    waiting_for_name = State()

class SavingsStates(StatesGroup):
    waiting_for_amount = State()

def main_menu_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📅 Habits")
    builder.button(text="💰 Savings")
    builder.button(text="🌐 Open Web-Panel")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        f"Hello, {message.from_user.first_name}! I'm Aster. \nChoose an option",
        reply_markup=main_menu_kb()
    )

@dp.message(F.text == "🌐 Open Web-Panel")
async def open_web(message: types.Message):
    url_with_id = f"{WEB_APP_URL}/?user_id={message.from_user.id}"
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Open Aster Core", web_app=WebAppInfo(url=url_with_id)))
    await message.answer("Your personal loggin", reply_markup=builder.as_markup())

@dp.message(F.text == "📅 Habits")
async def show_habits(message: types.Message):
    user_id = message.from_user.id
    habits = get_habits_for_today(date.today(), user_id)
    
    if not habits:
        await message.answer("No plans for today")
        return

    builder = InlineKeyboardBuilder()
    for h_id, name, status in habits:
        icon = "✅" if status else "⬜"
        builder.button(text=f"{icon} {name}", callback_data=f"toggle_{h_id}_{status}")
    
    builder.adjust(1)
    await message.answer("Your habits for today", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("toggle_"))
async def toggle_habit_callback(callback: types.callback_query):
    _, h_id, current_status = callback.data.split("_")
    new_status = 0 if int(current_status) == 1 else 1
    user_id = callback.from_user.id
    
    log_habit(int(h_id), date.today().isoformat(), new_status, user_id)
    
    habits = get_habits_for_today(date.today(), user_id)
    builder = InlineKeyboardBuilder()
    for h_id, name, status in habits:
        icon = "✅" if status else "⬜"
        builder.button(text=f"{icon} {name}", callback_data=f"toggle_{h_id}_{status}")
    builder.adjust(1)
    
    await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
    await callback.answer()

@dp.message(F.text == "💰 Savings")
async def savings_menu(message: types.Message):
    balance = get_current_balance(message.from_user.id)
    builder = InlineKeyboardBuilder()
    builder.button(text="Feed piggy", callback_data="add_savings")
    await message.answer(f"Current balance {balance}₴", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "add_savings")
async def ask_savings_amount(callback: types.callback_query, state: FSMContext):
    await state.set_state(SavingsStates.waiting_for_amount)
    await callback.message.answer("Enter amount:")
    await callback.answer()

@dp.message(SavingsStates.waiting_for_amount)
async def process_savings(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        user_id = message.from_user.id
        new_balance = get_current_balance(user_id) + amount
        feed_piggy_bank(amount, new_balance, user_id)
        await message.answer(f"Added, new balance: {new_balance}₴", reply_markup=main_menu_kb())
        await state.clear()
    except ValueError:
        await message.answer("Please, enter a number")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        print("Bot is active")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot isn't active")