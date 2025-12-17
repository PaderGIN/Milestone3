import asyncio
import logging
import os

import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import BufferedInputFile

TOKEN = os.getenv("TELEGRAM_TOKEN")
ML_API_URL = os.getenv("ML_API_URL", "http://ml_service:8000/predict")
STATS_URL = "http://ml_service:8000/stats"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

def draw_progress_bar(score: float) -> str:
    percent = int(score * 100)
    blocks = int(score * 10)
    bar = "🟩" * blocks + "⬜" * (10 - blocks)
    return f"{bar} {percent}%"

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()

    builder.button(text="Where is ETSII located?")
    builder.button(text="What is the grading system?")
    builder.button(text="Tell me about Erasmus")
    builder.button(text="How many ECTS for bachelor?")

    builder.button(text="📊 Statistics")

    builder.adjust(2, 2, 1)

    await message.answer(
        "🎓 **Welcome to Axiomus UPM Bot!**\n\n"
        "I am an AI assistant trained on Universidad Politécnica de Madrid data.\n"
        "I can answer questions about campuses, grades, and programs.\n\n"
        "👇 **Choose a question below or type your own:**",
        reply_markup=builder.as_markup(resize_keyboard=True),
        parse_mode="Markdown"
    )

async def send_analytics(message: types.Message):
    await message.answer("📊 **Generating Analytics Report...**", parse_mode="Markdown")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(STATS_URL) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    await message.answer_photo(
                        photo=BufferedInputFile(image_data, filename="stats.png"),
                        caption="📈 **Model Confidence Distribution**\nHere is how confident I was in my recent answers."
                    )
                else:
                    try:
                        error_json = await resp.json()
                        err_msg = error_json.get('error', 'Unknown error')
                    except:
                        err_msg = await resp.text()
                    await message.answer(f"⚠️ {err_msg}")

    except Exception as e:
        await message.answer(f"❌ Error fetching stats: {e}")

@dp.message(Command("stats"))
async def cmd_stats_handler(message: types.Message):
    await send_analytics(message)

@dp.message(F.text == "📊 Statistics")
async def btn_stats_handler(message: types.Message):
    await send_analytics(message)

@dp.message()
async def handle_message(message: types.Message):
    user = message.from_user
    full_name = f"{user.first_name} {user.last_name or ''}".strip()
    logging.info(f"👤 USER: {full_name} [ID:{user.id}] | ❓ ASKED: {message.text}")

    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    temp_msg = await message.answer("🧠 **Analyzing UPM Knowledge Base...**", parse_mode="Markdown")

    try:
        async with aiohttp.ClientSession() as session:
            payload = {"question": message.text}
            async with session.post(ML_API_URL, json=payload) as resp:
                if resp.status == 200:
                    res = await resp.json()
                    ans = res.get("answer")
                    score = res.get("score", 0.0)
                    context = res.get("context", "No context available.")

                    confidence_bar = draw_progress_bar(score)

                    response_text = (
                        f"🤖 **Answer:**\n{ans}\n\n"
                        f"📊 **Confidence:**\n{confidence_bar}\n\n"
                        f"📚 **Source Context:**\n>_{context}_"
                    )

                    feedback_kb = InlineKeyboardBuilder()
                    feedback_kb.button(text="👍 Good", callback_data="like")
                    feedback_kb.button(text="👎 Bad", callback_data="dislike")

                    await temp_msg.edit_text(
                        response_text,
                        parse_mode="Markdown",
                        reply_markup=feedback_kb.as_markup()
                    )
                else:
                    await temp_msg.edit_text(f"⚠️ **Service Error:** {resp.status}", parse_mode="Markdown")

    except Exception as e:
        await temp_msg.edit_text(f"❌ **Connection Error:**\n`{str(e)}`", parse_mode="Markdown")

@dp.callback_query(F.data.in_({"like", "dislike"}))
async def feedback_handler(callback: types.CallbackQuery):
    await callback.answer("Thanks for your feedback! (Saved to logs)")
    await callback.message.edit_reply_markup(reply_markup=None)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    if not TOKEN:
        print("Error: TELEGRAM_TOKEN is not set.")
    else:
        asyncio.run(main())