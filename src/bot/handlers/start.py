# Telegram handler which sending welcome text

from aiogram import types, Router
from aiogram.filters import Command, CommandObject, CommandStart
from bot.conf import config_tg
from utils import keyboards
import random
from services.db.user_group import auto_add
import base64
from urllib.parse import parse_qs

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message, command: CommandObject = None):
    payload = command.args if command and command.args else None
    print(command)
    print(payload)
    try:
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

    if payload:
        if payload.startswith("group"):
            b64_part = payload.split("_", 1)[1]
            rem = len(b64_part) % 4
            if rem > 0:
                b64_part += "=" * (4 - rem)
            
            try:
                decoded_bytes = base64.urlsafe_b64decode(b64_part)
                decoded_str = decoded_bytes.decode("utf-8")
                
                from services.db.user_group import set_user_group
                await set_user_group(message.from_user.id, decoded_str.capitalize())
                
                await message.answer(f"Привет! Группа <b>{decoded_str.capitalize()}</b> успешно установлена!", parse_mode="HTML")
            except Exception as e:
                print(e)
                
    await message.answer(
        text=welcome_text,
        message_effect_id=effect_id,
        reply_markup=kb,
        parse_mode="HTML"
    )
    # print(1)
    await auto_add(message.from_user.id)
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
