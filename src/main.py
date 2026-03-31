import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from bot.handlers import start, show_c, conv, schedule, set_group, profile, inline
from utils.anti_flood import AntiFloodMiddleware
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
dp.include_router(profile.router)
dp.include_router(inline.router)

# async def main():
#     await dp.start_polling(bot)

# if __name__ == "__main__":
#     asyncio.run(main())

async def start_bot():
    dp.update.outer_middleware(AntiFloodMiddleware(default_rate=1.5))
    await dp.start_polling(bot)

# app = Flask(__name__)

# @app.route("/health")
# def health_check():
#     return "OK", 200

# def run_http_server():
#     port = int(os.environ.get("PORT", 10000))
#     app.run(host="0.0.0.0", port=port)

import fastapi
from services.db import schedule as sch
from pathlib import Path
import json
import uvicorn
import threading
from services.db import user_group
from fastapi.middleware.cors import CORSMiddleware


app = fastapi.FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def f():
    return {"status": 200}


@app.get("/group/{tg_id}")
async def get_group(tg_id: int):
    data = await user_group.check_user_group(tg_id)
    if data:
        return data
    
    
@app.get("/schedule/{group}")
def get_schedule(group: str):
    resp = sch.Schedule(group_name=group).run_()
    codes = {}
    try:
        config_path = Path(__file__).parent.parent / "config" / "example-time.json"
        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)
            # print(data)
            for c in data["Times"]:
                codes[c["Code"]] = (
                    c["TimeFrom"][-8:-3],
                    c["TimeTo"][-8:-3],
                )
    except FileNotFoundError:
        print("example-time.json not found :(")
    if not resp:
        return "Пока что пусто"
    
    week_name, days_data = resp
    if not days_data:
        return "Пока что пусто"
    
    string = """"""
    for day, contents in days_data.items():
        for content in contents:
            if not content:
                continue
            string += f"""<div class='day'><h3 class='day-name'>{day}</h3>"""
            for lesson in content:
                time_code = lesson["time_code"]
                time_range = codes.get(time_code, ("", ""))
                string += (
                    f"<h4 class='lesson'>{lesson['time']}</h4>"
                    f"<h6 class='time'> {time_range[0]} - {time_range[1]}</h6>"
                )
                string += f"<span class='subject'>{lesson['subject']}</span> <span class='room'>({lesson["room"]})</span>"
                string += f"<h3 class='teacher'>{lesson['teacher']}</h3>"
            string += "</div>"
    if not string:
        return "Пока что пусто"
    
    return string

def run_api():
    # uvicorn.run(app, host="https://boost.rorosin.ru", port=443)
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    # http_thread = threading.Thread(target=run_http_server, daemon=True)
    # http_thread.start()
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    asyncio.run(start_bot())