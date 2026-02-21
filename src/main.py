import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from bot.handlers import start, show_c, conv, schedule, set_group
from flask import Flask
import threading

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# add here
dp.include_router(start.router)
dp.include_router(show_c.router)
dp.include_router(conv.router)
dp.include_router(set_group.router)
dp.include_router(schedule.router)


# async def main():
#     await dp.start_polling(bot)

# if __name__ == "__main__":
#     asyncio.run(main())

async def start_bot():
    await dp.start_polling(bot)

app = Flask(__name__)

@app.route("/health")
def health_check():
    return "OK", 200

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()

    asyncio.run(start_bot())