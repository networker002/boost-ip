from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F, Bot
from services.db import schedule
from services.db.user_group import check_user_group
from random import choice as r_choice
import json
from pathlib import Path

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


async def _get_schedule_logic(message: types.Message, user_id: int, bot: Bot):
    sent_message = await message.answer(r_choice(["Загружаю расписаие. Ожидайте...", "Расписание отправляется...", "Получаем расписание...", "Секунду... Расписание обрабатывается", "Ваше расписание почти готово..."]))

    res = await check_user_group(user_id)
    if res is None:
        await sent_message.edit_text("Сначала вы должны зарагестрировать свою группу.\nИспользуйте команду /group")
    else: 
        try:
            group_name = res.get("group_name")
            response = schedule.Schedule(group_name=group_name).run_()
        except Exception as e:
            print(e)
            response = None

        finally:
            try:
                config_path = Path(__file__).parent / "config" / "example-time.json"
                with open(config_path, encoding="utf-8") as f:
                    data = json.load(f)
                    codes = {}
                    for c in data["Times"]:
                        codes[c["Code"]] = c["TimeFrom"][-8:-3], c["TimeTo"][-8:-3]
            except FileNotFoundError: print(":(")
            string = """"""
            print(response)
            if response is not None and response[1]:
                for day in response[1]:
                    for content in response[1][day]:
                        string += "\n——————————————\n📅 <b>"+day+"</b>\n"
                        for lesson in content:
                            string += "\n⏰ <b>"+lesson["time"]+"</b> "+codes[lesson["time_code"]][0]+" - "+codes[lesson["time_code"]][1]+"\n"
                            string += "📚 "+lesson["subject"]+"\n"
            else:
                await sent_message.edit_text("Пока что пусто")
                
            await bot.unpin_all_chat_messages(message.chat.id)

            await sent_message.pin()
            await sent_message.edit_text(
                text=f"<b>Вот твое расписание</b>\n({response[0].capitalize()}){string}",
                parse_mode="HTML"
            ) if response != None else await sent_message.edit_text("Пока что пусто")
            