from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F
from services.db import schedule
from services.db.user_group import check_user_group
from random import choice as r_choice

router = Router()

class ScheduleState(StatesGroup):
    group_getting = State()


@router.message(Command("schedule"))
async def cmd_get_schedule(message: types.Message):
    await _get_schedule_logic(message, message.from_user.id)

@router.callback_query(F.data == "watch_schedule_btn")
async def btn_watch_schedule(callback: types.CallbackQuery):
    await _get_schedule_logic(callback.message, callback.from_user.id)
    await callback.answer() 


async def _get_schedule_logic(message: types.Message, user_id: int):
    
    sent_message = await message.answer(r_choice(["Загружаю расписаие. Ожидайте...", "Расписание отправляется", "Получаем расписание...", "Секунду", "Почти готово"]))

    res = check_user_group(user_id)
    if res is None:
        await sent_message.edit_text("Сначала вы должны зарагестрировать свою группу.\nИспользуйте команду /group")
    else: 
        try:
            group_name = res.get("group_name")
            response = schedule.Schedule(group_name=group_name).run_()[1]
        except Exception as e:
            print(e)
            response = "Пока что пусто"

        finally:
            await sent_message.edit_text(
                str(response)
            )