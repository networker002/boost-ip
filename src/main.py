import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from bot.handlers import start, show_c, conv, schedule, set_group, profile, inline
from utils.anti_flood import AntiFloodMiddleware
import threading
import hmac
import json
import time
from hashlib import sha256
from urllib.parse import parse_qsl

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
from services.db import user_group
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


class InitDataValidationError(Exception):
    pass


def validate_telegram_init_data(
    init_data_raw: str,
    bot_token: str,
    max_age_seconds: int = 300,
) -> dict:
    """
    Валидирует Telegram Mini App initData.

    :param init_data_raw: сырой window.Telegram.WebApp.initData
    :param bot_token: токен бота
    :param max_age_seconds: максимальный возраст auth_date в секундах
    :return: dict с распарсенными полями
    :raises InitDataValidationError: если данные невалидны
    """
    if not init_data_raw:
        raise InitDataValidationError("initData is empty")

    pairs = dict(parse_qsl(init_data_raw, keep_blank_values=True))

    received_hash = pairs.pop("hash", None)
    if not received_hash:
        raise InitDataValidationError("hash is missing")

    auth_date_raw = pairs.get("auth_date")
    if not auth_date_raw:
        raise InitDataValidationError("auth_date is missing")

    try:
        auth_date = int(auth_date_raw)
    except ValueError as e:
        raise InitDataValidationError("auth_date is invalid") from e

    now = int(time.time())
    if max_age_seconds > 0 and now - auth_date > max_age_seconds:
        raise InitDataValidationError("initData is expired")

    data_check_string = "\n".join(
        f"{key}={value}"
        for key, value in sorted(pairs.items(), key=lambda item: item[0])
    )

    secret_key = hmac.new(
        key=b"WebAppData",
        msg=bot_token.encode(),
        digestmod=sha256,
    ).digest()

    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=sha256,
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise InitDataValidationError("hash is invalid")

    if "user" in pairs:
        try:
            pairs["user"] = json.loads(pairs["user"])
        except json.JSONDecodeError as e:
            raise InitDataValidationError("user is not valid JSON") from e

    if "receiver" in pairs:
        try:
            pairs["receiver"] = json.loads(pairs["receiver"])
        except json.JSONDecodeError as e:
            raise InitDataValidationError("receiver is not valid JSON") from e

    if "chat" in pairs:
        try:
            pairs["chat"] = json.loads(pairs["chat"])
        except json.JSONDecodeError as e:
            raise InitDataValidationError("chat is not valid JSON") from e

    pairs["auth_date"] = auth_date
    return pairs


def authorize(raw_data: str):
    print(raw_data)
    try:
        validated_data = validate_telegram_init_data(raw_data, os.environ.get("TELEGRAM_BOT_TOKEN"))
    except InitDataValidationError:
        return None, "Init data is not valid"

    if "user" not in validated_data.keys():
        return None, "No user object in init data"

    user_group.auto_add(validated_data["user"]["id"])

    return validated_data, None


@app.get("/")
def f():
    return {"status": 200}


@app.get("/group")
async def get_group(request: fastapi.Request):
    auth_data, auth_err = authorize(request.headers.get("Authorization"))
    if auth_err is not None:
        return fastapi.Response(json.dumps({"error": auth_err}), 401)

    data = await user_group.check_user_group(auth_data["user"]["id"])
    if data:
        return data


@app.get("/schedule")
def get_schedule(request: fastapi.Request):
    auth_data, auth_err = authorize(request.headers.get("Authorization"))
    if auth_err is not None:
        return fastapi.Response(json.dumps({"error": auth_err}), 401)

    group = user_group.check_user_group(auth_data["user"]["id"])

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

    string = "Пока что пусто"
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
