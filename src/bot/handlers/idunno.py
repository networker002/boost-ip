import asyncio
import random
from aiogram import Bot, Router, F, types
from aiogram.types import Message
from aiogram.filters import BaseFilter, StateFilter
from aiogram.enums import ChatAction
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, WebAppInfo

from utils.command_list import get_command_list_text as get
from services import ai
from services.db.user_group import check_user_group
from services.db import schedule
from services import get_weeks

from pathlib import Path
import json
import io

import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

router = Router()
c_list = [cmd.strip().lower() for cmd in get().split("\n") if cmd.strip()]

builder = InlineKeyboardBuilder()
builder.row(InlineKeyboardButton(
        text="Открыть дневник", 
        web_app=WebAppInfo(url="https://networker002.github.io/webapp/")
    ))

TRIGGERS = ["расписан", "график", "урок", "пар", "заняти", "лекци", "распоряд", "план", "календар", "расп"]

class IdontKnowFilter(BaseFilter):
    
    async def __call__(self, message: Message) -> bool:
        return bool(message.text) and message.text.strip().lower() not in c_list

async def check_async(text: str) -> bool:
    if not text:
        return False
        
    text_lower = text.lower()
    words = text_lower.split()

    if any(any(word.startswith(t) for t in TRIGGERS) for word in words):
        return True

    try:
        return await asyncio.to_thread(ai.answer_text, text)
    except Exception as e:
        print(f"AI Check Error: {e}")
        return False


codes = {}
try:
    config_path = Path(__file__).parent.parent.parent.parent / "config" / "example-time.json"
    with open(config_path, encoding="utf-8") as f:
        data_ = json.load(f)
            #print(data)
        for c in data_["Times"]:
                codes[c["Code"]] = (
                    c["TimeFrom"][-8:-3],
                    c["TimeTo"][-8:-3],
                )
except FileNotFoundError:
    print("example-time.json not found :(")

@router.message(IdontKnowFilter(), StateFilter(None))
async def idunno(message: Message, bot: Bot):
    if message.chat.type == "private":
        await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
        await asyncio.sleep(0.5)
        await message.reply(
            "<b>Извините, я не понимаю эту команду</b>\n\n"
            "<i>Вот список доступных команд:</i>\n" + get(),
            parse_mode="HTML"
        )
    elif message.chat.type in ["group", "supergroup"]:
        answerId = await check_async(message.text)

        if answerId == True:
            res = await check_user_group(message.from_user.id)
            if res is None or len(res.get("group_name")) < 4:
                await message.reply(
                    text=f"{message.from_user.full_name.capitalize()}, сначала Вы должны зарегистрировать свою группу.\nИспользуйте команду /group"
                )
                return
            
            try:
                group_name = res.get("group_name")
                response1, response2, response3 = await schedule.Schedule(group_name=group_name).get_schedule_async(prev_next=True)
            except Exception as e:
                print(e)
            
            all_dates = get_weeks.get_range()
            req_days = []
            (color1, color2, color3) = random.choice([
                ("#27AE60", "#1D8348", "#D5F5E3"),
                ("#279EAE", "#1D5283", "#D5E2F5"),
                ("#8827AE", "#5A1D83", "#EFD5F5"),
                ("#AEAC27", "#A0AF19", "#F5F5D5")
            ])
            for week in all_dates:
                for day in week:
                    req_days.append(day)
                
            from PIL import Image, ImageDraw, ImageFont
            import textwrap
            import os
            try:
                font_path = os.path.join(os.path.dirname(__file__), "Roboto-Regular.ttf")
                font_title = ImageFont.truetype(font_path, 28)
                font_week = ImageFont.truetype(font_path, 22)
                font_day = ImageFont.truetype(font_path, 20)
                font_text = ImageFont.truetype(font_path, 18)
                font_small = ImageFont.truetype(font_path, 14)
            except OSError:
                font_title = font_week = font_day = font_text = font_small = ImageFont.load_default()

            responses = [response1, response2, response3]
            
            media_list = []

            for idx, response in enumerate(responses):
                if not response: continue
                    
                week_name, days_data = response
                current_week_dates = all_dates[idx] if idx < len(all_dates) else []


                valid_days_to_draw = []
                for day_idx, (day_name, lessons) in enumerate(days_data.items()):
                    date_str = current_week_dates[day_idx] if day_idx < len(current_week_dates) else ""
                    if req_days and date_str not in req_days:
                        continue
                    valid_days_to_draw.append((day_name, date_str, lessons))


                if not valid_days_to_draw:
                    continue


                width = 1200 

                temp_img = Image.new('RGB', (width, 5000), color='#f4f7f2')
                draw = ImageDraw.Draw(temp_img)
                
                y = 20
                draw.text((20, y), f"Расписание: {group_name}", fill="#2d3436", font=font_title)
                y += 60

                draw.rounded_rectangle([20, y, width-20, y+45], radius=8, fill=color1)
                draw.text((40, y+10), str(week_name), fill="white", font=font_week)
                y += 70

                col_x = [20, 610]
                col_w = 570
                col_y = [y, y]
                
                for d_idx, (day_name, date_str, lessons) in enumerate(valid_days_to_draw):
                    c_idx = d_idx % 2
                    c_x = col_x[c_idx]

                    draw.rounded_rectangle([c_x, col_y[c_idx], c_x + col_w, col_y[c_idx]+35], radius=6, fill=color3)
                    draw.text((c_x + 20, col_y[c_idx] + 5), f"{day_name} ({date_str})", fill=color2, font=font_day)
                    col_y[c_idx] += 45

                    if not lessons:
                        draw.text((c_x + 20, col_y[c_idx]), "Пар нет", fill="#7F8C8D", font=font_text)
                        col_y[c_idx] += 40
                    else:
                        for lesson in lessons:
                            t_code = int(lesson.get("time_code", 0))
                            t_range = codes.get(t_code, ("??:??", "??:??"))
                            time_str = f"· {t_range[0]} - {t_range[1]}"
                            
                            draw.text((c_x + 20, col_y[c_idx]), time_str, fill="#34495E", font=font_text)
                            col_y[c_idx] += 25
                            
                            subj = f"{lesson.get('subject', '---')} ({lesson.get('room', '-')})"
                            wrapped_subject = textwrap.wrap(subj, width=40) 
                            for line in wrapped_subject:
                                draw.text((c_x + 40, col_y[c_idx]), line, fill="#2d3436", font=font_text)
                                col_y[c_idx] += 25
                            
                            teacher = f"{lesson.get('teacher', '---')}"
                            draw.text((c_x + 40, col_y[c_idx]), teacher, fill="#7F8C8D", font=font_small)
                            col_y[c_idx] += 25
                            
                            draw.line([c_x + 20, col_y[c_idx], c_x + col_w - 20, col_y[c_idx]], fill="#BDC3C7", width=1)
                            col_y[c_idx] += 15
                    
                    col_y[c_idx] += 20 


                final_y = max(col_y[0], col_y[1]) + 20 
                week_img = temp_img.crop((0, 0, width, max(final_y, 300)))

                path = io.BytesIO()
                week_img.save(path, format='PNG')
                path.seek(0)
                file = types.BufferedInputFile(path.getvalue(), filename=f"week_{idx+1}.png")
                media_list.append(types.InputMediaPhoto(
                    media=file,
                    caption=f"<b>📅 Вот расписание</b>\n1) Прошедшая неделя\n2) Текущая неделя\n3) Будущая неделя\nНадеюсь, помог" if responses[-1] == response else None, parse_mode="HTML"
                ))
                # await callback.message.answer_photo(
                #     photo=types.BufferedInputFile(path.getvalue(), filename=f"week_{idx+1}.png"),
                #     caption=f"📅 {week_name}\nГруппа: <b>{group_name}</b>",
                #     parse_mode="HTML"
                # )
            if media_list:
                await message.reply_media_group(media=media_list)
            else:
                print("unk err")
            
            try:
                st_TXT = []
                st_cfg_txt = {} #txt
                full_week_txt = ""
                
                for idx, response in enumerate([response1, response2, response3]):
                    
                    current_week_by_dates = all_dates[idx]
                    week_name, days_data = response
                    st_cfg_txt[week_name] = {}
                    
                    
                    for day_idx, (dayN, dayC) in enumerate(days_data.items()):
                        stringTXT = """"""
                        # if dayN == "Понедельник":
                        #     stringHTML += "<div class='week'>"
                        stringTXT += f"\t📆 {dayN} {current_week_by_dates[day_idx] if  day_idx < len(current_week_by_dates) else ""}\n"
                        
                        if not dayC:
                            stringTXT += "\nЗанятий нет\n"
                        else:
                            for lesson in dayC:
                                time_code = int(lesson["time_code"])
                                time_range = codes.get(time_code, ("", ""))
                                
                                stringTXT += (
                                    f"\n{lesson['time']}\n"
                                    f"  {time_range[0]} - {time_range[1]}\n"
                                    f"  {lesson['teacher']}\n"
                                    f"  {lesson['subject']} ({lesson['room']})\n"
                                )
                        stringTXT += "\n"
                        
                        if day_idx < len(current_week_by_dates):
                            date_key = current_week_by_dates[day_idx]
                            st_cfg_txt[week_name][date_key] = stringTXT

                    full_week_txt += "\n" + "\n".join(st_cfg_txt[week_name].values())
                    st_TXT.append(full_week_txt)

                
                ans2 = ai.answer_text_with_fallback(message.text, full_week_txt)

                await message.reply(
                    f"<b>🤖 AI анализ</b>:\n\n<blockquote>{ans2}</blockquote>",
                    parse_mode="HTML"
                )
            except Exception as e:
                print("idunno.py, 230")
                print(e)

@router.message(F.sticker)
async def and_st(message: Message):
    s_id = "CAACAgEAAxkDAAIC02n8kf4y4mOHy7Ve0F7Q_NsFCS7SAAJtCwACxZ3oRwVDI0xmpxilOwQ"
    if message.sticker.file_id != s_id:
        await message.react([types.ReactionTypeEmoji(emoji="👍")])
        await message.reply_sticker(s_id)
    elif message.sticker.file_id == s_id:
        await message.reply("Нет. Это мой стикер!\nЛучше посмотри расписание 👌", reply_markup=builder.as_markup())