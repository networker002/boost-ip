from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv
import os
from services.db.user_group import check_user_group, set_user_group
from utils import keyboards, validate_group


load_dotenv()


ACCESS_KEY = os.getenv("GROUP_SECRET")
if not ACCESS_KEY:
    raise ValueError("GROUP_SECRET not set in .env")



class GroupState(StatesGroup):
    wanting_crate_group = State()
    waiting_for_code = State()



class EditingGroup(StatesGroup):
    waiting_new_group = State()



router = Router()



@router.message(Command("group"))
async def check_group(message: types.Message):
    check_data = await check_user_group(message.from_user.id)

    if check_data["group_name"].upper() not in ["NULL", ""]:
        keyboard_schedule = keyboards.watch_schedule_edit_group_kb()
        await message.answer(f"Ваша группа - <b>{check_data['group_name']}</b>", parse_mode="HTML", reply_markup=keyboard_schedule)
    

    else:
        kb = keyboards.yes_no_group_want_kb()
        await message.answer(
            "Вы еще не зарегестрировали группу. <b>Желаете это сделать?</b>",
            parse_mode="HTML",
            reply_markup=kb
        )
        
    
@router.callback_query(F.data == "want_add_group")
async def pre_code(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Пожалуйста, введите код для активации:")
    await state.set_state(GroupState.waiting_for_code)
    await callback.answer()



@router.message(F.text, GroupState.waiting_for_code)
async def check_code(message: types.Message, state: FSMContext):
    user_nput = message.text


    if ACCESS_KEY == user_nput:
        await message.reply("Супер! Код успешно активирован. Теперь введите свою группу - я вас зарегестрирую: ")
        await state.set_state(GroupState.wanting_crate_group)
    else: await message.reply("Упс! Возможно, код неправильный. Пожалуйста, перепроверьте данные или обратитесь в поддержку")
    # await message.answer()


@router.message(F.text, GroupState.wanting_crate_group)
async def set_group(message: types.Message, state: FSMContext):
    group_name = message.text.strip()
    is_valid, msg = validate_group.val_gr_n(group_name)
    
    if not is_valid:
        await message.answer(msg)
        return
    
    if await set_user_group(message.from_user.id, group_name):
        await state.clear()
        await message.answer("Группа успешно установлена!")
    else:
        await message.answer("Ошибка сохранения. Попробуйте позже.")


@router.callback_query(F.data == "dont_want_add_group")
async def dont_notice_cr_group(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Хорошо. Чтобы узнать расписание, вы должны указать группу (потом можно ее изменить)")
    await callback.answer("Регестрация отменена")



@router.callback_query(F.data == "edit_group_btn")
async def watch_schedule_edit_by_btn(callback: types.CallbackQuery, state: FSMContext):
    if await check_user_group(tg_id=int(callback.from_user.id)) is not None:
        await callback.message.edit_text("Введите новую группу: ")
        await state.set_state(EditingGroup.waiting_new_group)
        await callback.answer()
    else:
        await callback.answer("Сначала зарегистрируйте группу!", show_alert=True)



@router.message(F.text, EditingGroup.waiting_new_group)
async def edit_schedule(message: types.Message, state: FSMContext):
    new_group = message.text.strip()

    is_valid, msg = validate_group.val_gr_n(new_group)
    if not is_valid:
        await message.answer(msg)
        return

    if await set_user_group(tg_id=message.from_user.id, group_name=new_group):
        await state.clear()
        await message.answer(
            f"Успешно! Новая группа - <b>{new_group}</b>",
            parse_mode="HTML",
            reply_markup=keyboards.watch_schedule_edit_group_kb()
        )
    else:
        await message.answer("Ошибка сохранения. Попробуйте позже.")