from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from services.db import schedule
from services.db.user_group import check_user_group
from random import choice as r_choice
import json
from pathlib import Path
from aiogram.exceptions import TelegramBadRequest
from utils import keyboards

router = Router()


class ScheduleState(StatesGroup):
    group_getting = State()

mrkp = None

@router.message(Command("schedule"))
async def cmd_get_schedule(message: types.Message, bot: Bot):
    await _get_schedule_logic(message, message.from_user.id, bot)


@router.callback_query(F.data == "watch_schedule_btn")
async def btn_watch_schedule(callback: types.CallbackQuery, bot: Bot):
    await _get_schedule_logic(callback.message, callback.from_user.id, bot)
    await callback.answer()


async def _safe_edit_text(msg: types.Message, text: str, **kwargs):
    if msg.text == text:
        return msg
    try:
        return await msg.edit_text(text, **kwargs)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            return msg
        raise


async def _get_schedule_logic(message: types.Message, user_id: int, bot: Bot, weektype:int = 1, sent_message = None):
    if not sent_message:
        sent_message = await message.answer(
            r_choice([
                "Загружаю расписание. Ожидайте...",
                "Расписание отправляется...",
                "Получаем расписание...",
                "Секунду... Расписание обрабатывается",
                "Ваше расписание почти готово..."
        ])
        
    )
        
        s_data = True
    
    else:
        s_data = False

    res = await check_user_group(user_id)
    if res is None:
        await _safe_edit_text(
            sent_message,
            text="Сначала вы должны зарегистрировать свою группу.\nИспользуйте команду /group"
        )
        return
    
    try:
        group_name = res.get("group_name")
        # response = schedule.Schedule(group_name=group_name).run_()
        response1, response2, response3 = await schedule.Schedule(group_name=group_name).get_schedule_async(prev_next=True)
        #print(63)
    except Exception as e:
        print("Schedule error:", e)
        response1, response2, response3 = None, None, None

    codes = {}
    try:
        config_path = Path(__file__).parent.parent.parent.parent / "config" / "example-time.json"
        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)
            #print(data)
            for c in data["Times"]:
                codes[c["Code"]] = (
                    c["TimeFrom"][-8:-3],
                    c["TimeTo"][-8:-3],
                )
    except FileNotFoundError:
        print("example-time.json not found :(")
    # print(80)
    # print(response)
    #print(codes)
    st = []
    stWeek = []
    
    if not response2:
        await _safe_edit_text(sent_message, "Пока что пусто")
        return
    
    #print([response1, response2, response3])
    for response in [response1, response2, response3]:
        string = """"""
        week_name, days_data = response
        if not days_data:
            await _safe_edit_text(sent_message, "Пока что пусто")
            return
        string += "("+week_name+")"
        stWeek.append(week_name)
        for day, contents in days_data.items():
            if len(contents) == 0:
                pass
            else:
                string += f"""\n\n——————————————\n📅 <b>{day}</b>"""
            for lesson in contents:
                time_code = int(lesson["time_code"])
                # print(100)
                time_range = codes.get(time_code, ("", ""))
                # print(time_range)
                string += (
                    f"\n\n<b>{lesson['time']}</b>"
                    f" {time_range[0]} - {time_range[1]}\n"
                )
                string += f"{lesson['subject']} ({lesson['room']})"
        st.append(string)

    if not st:
        await _safe_edit_text(sent_message, "Пока что пусто")
        return

    try:
        await bot.unpin_all_chat_messages(message.chat.id)
    except TelegramBadRequest:
        pass

    try:
        if s_data:
            await sent_message.pin()
    except TelegramBadRequest:
        pass
    
    mapping = {
    0: "1 числитель",
    1: "1 знаменатель",
    2: "2 числитель",
    3: "2 знаменатель"
    }
    
    # mapping_prev = {
    #     0:3,
    #     1:0,
    #     2:1,
    #     3:2
    # }
    
    # mapping_next = {
    #     0:1,
    #     1:2,
    #     2:3,
    #     3:0
    # }

    final_text = f"<b>Вот твое расписание</b>\n{st[weektype]}"
    mappingPR = {
        0: None,
        1: stWeek[0],
        2: stWeek[1]
    }
    
    mappingNX = {
        0: stWeek[1],
        1: stWeek[2],
        2: None
    }
    pr =  mappingPR.get(weektype)
    nx = mappingNX.get(weektype)
    
    # print(pr, nx)

    if weektype == 1:
        prev_cb = "swipe_week:0"
        next_cb = "swipe_week:2"
    elif weektype == 0:
        prev_cb = None
        next_cb = "swipe_week:1"
    else:
        prev_cb = "swipe_week:1"
        next_cb = None

    mrkp = keyboards.swipe_schedule_kb(pr, nx, prev_data=prev_cb or "prev_week", next_data=next_cb or "next_week")
    #print(stWeek)
    await _safe_edit_text(sent_message, final_text, parse_mode="HTML", reply_markup=mrkp)

@router.callback_query(F.data.startswith("swipe_week:"))
async def swipe_schedule(callback: types.CallbackQuery, bot: Bot):
    try:
        weektype = int(callback.data.split(":", 1)[1])
    except (ValueError, IndexError):
        await callback.answer()
        return
    await _get_schedule_logic(callback.message, callback.from_user.id, bot, weektype=weektype, sent_message=callback.message)
    M = {
        "0": "Предыдущая неделя",
        "1": "Текущая неделя",
        "2": "Следующая неделя"
    }
    await callback.answer(M.get(callback.data[-1]))

@router.callback_query(F.data == "prev_week")
async def go_prev_sc(callback: types.CallbackQuery, bot: Bot):
    await _get_schedule_logic(callback.message, callback.from_user.id, bot, weektype=0, sent_message=callback.message)

@router.callback_query(F.data == "next_week")
async def go_prev_sc(callback: types.CallbackQuery, bot: Bot):
    await _get_schedule_logic(callback.message, callback.from_user.id, bot, weektype=2, sent_message=callback.message)