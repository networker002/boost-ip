from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from services.db import schedule
from services.db.user_group import check_user_group
from random import choice as r_choice
import json
from pathlib import Path
from aiogram.exceptions import TelegramBadRequest

router = Router()


class ScheduleState(StatesGroup):
    group_getting = State()


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


async def _get_schedule_logic(message: types.Message, user_id: int, bot: Bot):
    sent_message = await message.answer(
        r_choice([
            "Загружаю расписаие. Ожидайте...",
            "Расписание отправляется...",
            "Получаем расписание...",
            "Секунду... Расписание обрабатывается",
            "Ваше расписание почти готово..."
        ])
    )

    res = await check_user_group(user_id)
    if res is None:
        await _safe_edit_text(
            sent_message,
            text="Сначала вы должны зарегистрировать свою группу.\nИспользуйте команду /group"
        )
        return
    
    try:
        group_name = res.get("group_name")
        response = schedule.Schedule(group_name=group_name).run_()
        # print(61)
        # print(response)
    except Exception as e:
        print("Schedule error:", e)
        response = None

    codes = {}
    try:
        config_path = Path(__file__).parent.parent.parent.parent / "config" / "example-time.json"
        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)
            print(data)
            for c in data["Times"]:
                codes[c["Code"]] = (
                    c["TimeFrom"][-8:-3],
                    c["TimeTo"][-8:-3],
                )
    except FileNotFoundError:
        print("example-time.json not found :(")
    # print(80)
    # print(response)
    if not response:
        await _safe_edit_text(sent_message, "Пока что пусто")
        return

    week_name, days_data = response
    if not days_data:
        await _safe_edit_text(sent_message, "Пока что пусто")
        return
    
    string = """"""
    for day, contents in days_data.items():
        for content in contents:
            if not content:
                continue
            string += f"""\n\n——————————————\n📅 <b>{day}</b>"""
            for lesson in content:
                time_code = lesson["time_code"]
                # print(100)
                time_range = codes.get(time_code, ("", ""))
                # print(time_range)
                string += (
                    f"\n\n⏰ <b>{lesson['time']}</b>"
                    f" {time_range[0]} - {time_range[1]}\n"
                )
                string += f"📚 {lesson['subject']}"

    if not string:
        await _safe_edit_text(sent_message, "Пока что пусто")
        return

    try:
        await bot.unpin_all_chat_messages(message.chat.id)
    except TelegramBadRequest:
        pass

    try:
        await sent_message.pin()
    except TelegramBadRequest:
        pass

    final_text = f"<b>Вот твое расписание</b>\n({str(week_name).capitalize()}){string}"
    await _safe_edit_text(sent_message, final_text, parse_mode="HTML")