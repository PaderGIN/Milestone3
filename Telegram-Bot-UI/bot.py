import asyncio
import logging
import os

import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

TOKEN = os.getenv("TELEGRAM_TOKEN")
ML_API_URL = os.getenv("ML_API_URL", "http://ml_service:8000/predict")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Hello! I am the Axiomus UPM Bot.\n\n"
        "I know everything about Universidad Politécnica de Madrid.\n"
        "Ask me anything!"
    )

@dp.message()
async def handle_message(message: types.Message):
    question = message.text
    msg = await message.answer("🤔 Searching UPM database...")

    try:
        async with aiohttp.ClientSession() as session:
            payload = {"question": question}
            async with session.post(ML_API_URL, json=payload) as resp:
                if resp.status == 200:
                    res = await resp.json()
                    ans = res.get("answer")
                    score = res.get("score")

                    await msg.edit_text(f"**Answer:** {ans}\n\n*(Confidence: {score:.2f})*", parse_mode="Markdown")

    except Exception as e:
        await msg.edit_text(f"❌ Connection Error: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    if not TOKEN:
        print("Error: TELEGRAM_TOKEN is not set.")
    else:
        asyncio.run(main())