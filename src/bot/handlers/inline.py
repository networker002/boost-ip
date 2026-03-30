from aiogram import F, Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from hashlib import md5
from services.db import schedule, user_group
from pathlib import Path
import json

router = Router()

days_map = {
        "пн": "Понедельник", "понедельник": "Понедельник",
        "вт": "Вторник", "вторник": "Вторник",
        "ср": "Среда", "среда": "Среда",
        "чт": "Четверг", "четверг": "Четверг",
        "пт": "Пятница", "пятница": "Пятница",
        "сб": "Суббота", "суббота": "Суббота",
        "":["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
    }



@router.inline_query()
async def schedule_inline(inline_query: InlineQuery):
    text = inline_query.query.strip().lower()
    result_id = md5(text.encode()).hexdigest()
    print(text)
    print(result_id)
    group = await user_group.check_user_group(inline_query.from_user.id)
    group_name = group.get("group_name", "ИС-25-14О")
    
    codes = {}
    counter = 0
    d2 = 0
    try:
        config_path = Path(__file__).parent.parent.parent.parent / "config" / "example-time.json"
        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)
            for c in data["Times"]:
                codes[c["Code"]] = (
                        c["TimeFrom"][-8:-3],
                        c["TimeTo"][-8:-3],
                    )
    except FileNotFoundError:
        print("example-time.json not found :(")

    thumbnail_url = None
    try:
        target_day_code = days_map[text]

    except Exception:
        result_id = md5(text.encode()).hexdigest()
        res = InlineQueryResultArticle(
            id=result_id,
            title="День не найден",
            input_message_content=InputTextMessageContent(
                message_text=f"Неизвестный день: <b>{text}</b>\n\nПопробуйте: пн, вт, ср, чт, пт, сб",
                parse_mode="HTML"
            ),
            description="Введите корректный день недели"
        )
        await inline_query.answer(results=[res], cache_time=30)
        
        return
    
    try:
        
        week_type, sc = await schedule.Schedule(group_name=group_name).get_schedule_async()
        if type(target_day_code) == list:
            result = sc
        else:
            result = sc.get(target_day_code)
        string = """"""
        if text in [" " * x for x in range(0, 13)] or text in ["нед", "неделя"]:
            text = "неделя" 
            for day, contents in result.items(): 
                for content in contents:
                    if not content:
                        continue
                    if counter == 0:
                        string += f"""\n\n<blockquote>——————————————\n📅 <b>{day}</b>"""
                    
                    else:
                        string += f"""\n\n——————————————\n📅 <b>{day}</b>"""

                    counter += 1

                    for lesson in content:
                        time_code = lesson["time_code"]
                        # print(100)
                        time_range = codes.get(time_code, ("", ""))
                        # print(time_range)
                        string += (
                            f"\n\n<b>{lesson['time']}</b>"
                            f" {time_range[0]} - {time_range[1]}\n"
                        )
                        string += f"{lesson['subject']} ({lesson['room']})"
        else:
            for lesson in result[0]:
                #lesson = content
                time_code = lesson["time_code"]
                    # print(100)
                time_range = codes.get(time_code, ("", ""))
                    # print(time_range)
                if d2 == 0:
                    string += (
                            f"\n\n<blockquote><b>{lesson['time']}</b>"
                            f" {time_range[0]} - {time_range[1]}\n"
                        )
                    
                else:
                    string += (
                            f"\n\n<b>{lesson['time']}</b>"
                            f" {time_range[0]} - {time_range[1]}\n"
                        )
                d2 += 1
                string += f"{lesson['subject']} ({lesson["room"]})"
        print(week_type)
        print(counter, d2)
        print(string)
        print(result)
    except Exception as e:
        result_id = md5(text.encode()).hexdigest()
        res = InlineQueryResultArticle(
            id=result_id,
            title=f"Расписания на день {target_day_code} нет",
            input_message_content=InputTextMessageContent(
                message_text=f"Здесь пусто...",
                parse_mode="HTML"
            ),
            description="Значит - выходной!"
        )
        print(week_type)
        print(e)
        print(string)
        await inline_query.answer(results=[res], cache_time=30)
        return
    
    print(result)
    result_id = md5(text.encode()).hexdigest()
            
    if result is None:
        description_text = "Расписание на этот день не найдено"
        content_text = f"<b>{text}</b>\n\nНет данных."
        thumbnail_url = "https://img.icons8.com/?size=100&id=45967&format=png&color=000000"
    else:
        description_text = f"Расписание найдено"
        content_text = f"<b>📆 {", ".join(target_day_code) if type(target_day_code) == list else target_day_code}</b>\n<b>{str(week_type).title()}</b>\n{string}</blockquote>"
        thumbnail_url = "https://img.icons8.com/?size=100&id=D45ofLrj1Mp5&format=png&color=000000"

    res = InlineQueryResultArticle(
        id=result_id,
        title=f"Расписание: {text.upper()}",
        input_message_content=InputTextMessageContent(
            message_text=content_text,
            parse_mode="HTML"
        ),
        description=description_text,
        thumbnail_url=thumbnail_url
    )
    
    await inline_query.answer(results=[res], cache_time=60)
    