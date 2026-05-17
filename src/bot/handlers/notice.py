import asyncio

from aiogram import types, Router, Bot
from aiogram.filters import Command
from services.db import user_group

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils import keyboards

import json
from pathlib import Path
from services.db.client import supabase

router = Router()

try:
    with open(Path(__file__).parent.parent.parent.parent / "config" / "groups.json", "r", encoding="utf-8") as f:
        groups = json.load(f)
        groups = groups.get("groups", [])
except FileNotFoundError:
    print("groups.json not found. Please create the file and add group information.")
    
class NoticeState(StatesGroup):
    wanting_to_repeat = State()

@router.message(Command("notice"))
async def notice_handler(message: types.Message, bot: Bot, state: FSMContext):
    user_id = message.from_user.id
    
    text = message.text.split()
    #print(f"Received notice command from user {user_id} with text: {text}")
    #print(text[1:])
    if len(text) < 2:
        await message.reply("Пожалуйста, укажите группу и текст уведомления в формате:\n/notice [группа] [текст_уведомления]\n\n<tg-spoiler>Пример:\n/notice ИВБО-01 Встреча в 15:00 в аудитории 101</tg-spoiler>", parse_mode="HTML")

    else:
        try:
            group_name = ""
            idx = 0
            for i in text[1:]:
                gr = i.upper()
                if gr in groups:
                    group_name = gr
                    #print(f"Identified group name: {group_name}")
                    idx = text.index(i)
                    break
                
            del(text[idx])
            del(text[text.index("/notice")])
            data_to_send = " ".join(text).capitalize()
            
            if group_name:
                resp = await user_group.async_execute_supabase_call(
                    lambda: supabase.table("user_groups").select("tg_id").eq("group_name", group_name).execute()
                )
                
                status_message = await message.reply("Ищу пользователей...", parse_mode="HTML")
                
                if resp.data:
                    users = [user["tg_id"] for user in resp.data]
                    #print(users)
                    if len(users) > 0:
                        counter = 0
                        for tg_id in users:
                            try:
                                await bot.send_message(chat_id=int(tg_id), text=f"<b>Вам пришло уведомление от преподавателя:</b> \n\n<blockquote>{data_to_send}</blockquote>", parse_mode="HTML")
                                await asyncio.sleep(0.1)  # Добавляем небольшую задержку между отправкой сообщений
                                counter += 1
                            except Exception as e:
                                continue
                            
                        await status_message.edit_text(f"✅ Уведомление успешно отправлено группе <b>{group_name}</b>.\n<b>Получателей:</b> {counter}.", parse_mode="HTML", reply_markup=keyboards.want_to_repeat_kb())
                        await state.set_state(NoticeState.wanting_to_repeat)
                        await state.set_data({"group_name": group_name, "data_to_send": data_to_send})
                    else:
                        await status_message.edit_text(f"⚠️ Не удалось найти пользователей в группе <b>{group_name}</b>.", parse_mode="HTML")
                else:
                    await status_message.edit_text(f"⚠️ Не удалось найти пользователей в группе <b>{group_name}</b>.", parse_mode="HTML")
        except Exception as e:
            print(f"Error in notice_handler: {e}")
            await message.reply("Произошла ошибка при отправке уведомления. <b>Пожалуйста, проверьте правильность команды и попробуйте снова.</b>\n\n<tg-spoiler>Как пользоваться командой:\n/notice [группа] [текст_уведомления]</tg-spoiler>", parse_mode="HTML")
                
@router.callback_query(lambda c: c.data == "want_to_repeat")
async def repeat_notice_callback(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    current_state = await state.get_state()
    current_data = await state.get_data()
    #print(f"Current state in repeat_notice_callback: {current_state}")
    
    
    if current_state == NoticeState.wanting_to_repeat.state:
        if current_data:
            group_name = current_data.get("group_name")
            data_to_send = current_data.get("data_to_send")
            
            if group_name and data_to_send:
                resp = await user_group.async_execute_supabase_call(
                    lambda: supabase.table("user_groups").select("tg_id").eq("group_name", group_name).execute()
                )
                
                if resp.data:
                    users = [user["tg_id"] for user in resp.data]
                    counter = 0
                    for tg_id in users:
                        try:
                            await bot.send_message(chat_id=int(tg_id), text=f"<b>(2) Вам пришло уведомление от преподавателя:</b> \n\n<blockquote>{data_to_send}</blockquote>", parse_mode="HTML")
                            await asyncio.sleep(0.1)  # Добавляем небольшую задержку между отправкой сообщений
                            counter += 1
                        except Exception as e:
                            continue
                    
                    await callback.message.edit_text(f"✅ Уведомление успешно повторно отправлено группе <b>{group_name}</b>.\n<b>Получателей:</b> {counter}.", parse_mode="HTML")
                else:
                    await callback.message.edit_text(f"⚠️ Не удалось найти пользователей в группе <b>{group_name}</b>.", parse_mode="HTML")
            else:
                await callback.message.edit_text("⚠️ Не удалось получить данные для повторного уведомления.", parse_mode="HTML")
                
        await state.clear()