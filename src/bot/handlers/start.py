# Telegram handler which sending welcome text

from aiogram import types, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, WebAppInfo
from bot.conf import config_tg
from utils import keyboards
import random
from services.db.user_group import auto_add
import base64
#from urllib.parse import parse_qs
from services import get_gr_names

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message, command: CommandObject = None):
    payload = command.args if command and command.args else None
    #print(command)
    #print(payload)
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Смотреть расписание 🚀", 
        web_app=WebAppInfo(url="https://networker002.github.io/webapp/")
    ))
    
    try:
        try:
            await message.react("🏆")
        except:
            await message.react([types.ReactionTypeEmoji(emoji="🏆")])
            
    except AttributeError:
        pass

    if config_tg.stickers_greeting:
        try:
            await message.answer_sticker(sticker=random.choice(config_tg.stickers_greeting))
        except IndexError:
            # logger
            pass

    welcome_text = f"Привет, {message.from_user.first_name.capitalize()}! Я <b>BoostBot</b> <tg-emoji emoji-id='5445284980978621387'>🚀</tg-emoji>\nНажми на кнопку ниже, чтобы увидеть что я могу\n\n<b><tg-emoji emoji-id='5382357040008021292'>📦</tg-emoji> Или вопользуйтесь нашим приложением 🔥</b>"
    

    kb = keyboards.get_commands_kb()

    effect_id = None
    if config_tg.message_effects:
        try:
            effect_id = random.choice(config_tg.message_effects)
        except Exception: effect_id = None
        
    await auto_add(message.from_user.id)
    
    #print(f"User {message.from_user.id} started the bot. Payload: {payload}")
    
    if payload:
        if not payload.startswith("group_"):
            await message.answer(f"<b>Неизвестный payload!</b>\n\nПривет! Похоже, что ты перешёл по некорректной ссылке. Пожалуйста, убедись, что ссылка правильная и попробуй снова.", parse_mode="HTML")
            return
        
        if payload.startswith("group"):
            b64_part = payload.split("_", 1)[1]
            #print(b64_part)
            rem = len(b64_part) % 4
            if rem > 0:
                b64_part += "=" * (4 - rem)
            
            try:
                decoded_bytes = base64.urlsafe_b64decode(b64_part)
                decoded_str = decoded_bytes.decode("utf-8")
                #print(decoded_str)
                groups_list = get_gr_names.get_groups()
                
                if decoded_str.upper() not in groups_list:
                    await message.answer(f"Группа <b>{decoded_str.upper()}</b> не найдена в списке доступных групп. Пожалуйста, проверьте данные группы.", parse_mode="HTML")
                    return
                elif decoded_str.upper() in groups_list:                    
                    from services.db.user_group import set_user_group
                    added = await set_user_group(message.from_user.id, decoded_str.upper())   
                    if not added:
                        await message.answer(f"Произошла ошибка при установке группы <b>{decoded_str.upper()}</b>. Пожалуйста, попробуйте снова позже.", parse_mode="HTML")
                        return
                    elif added:
                        await message.answer(f"Привет! Группа <b>{decoded_str.upper()}</b> успешно установлена!", parse_mode="HTML", reply_markup=builder.as_markup())
                        
                    
            except Exception as e:
                print(e)
                await message.answer(f"Произошла ошибка при обработке ссылки. Пожалуйста, попробуйте снова позже.", parse_mode="HTML")
    else:
        await message.answer(
            text=welcome_text,
            message_effect_id=effect_id,
            reply_markup=kb,
            parse_mode="HTML"
        )
    # print(1)
    # print(message.from_user.id)
    # print(d)
    # print("done")


@router.callback_query(lambda c: c.data == "go_back_commands")
async def back_to_start(callback: types.CallbackQuery):

    kb = keyboards.get_commands_kb()
    
    welcome_text = f"Привет, {callback.from_user.first_name.capitalize()}! Я <b>BoostBot</b> <tg-emoji emoji-id='5445284980978621387'>🚀</tg-emoji>\nНажми на кнопку ниже, чтобы увидеть что я могу\n\n<b><tg-emoji emoji-id='5382357040008021292'>📦</tg-emoji> Или вопользуйтесь нашим приложением 🔥</b>"
    await callback.message.edit_text(
        welcome_text,
        reply_markup=kb,
        parse_mode="HTML"
    )
    await callback.answer()
