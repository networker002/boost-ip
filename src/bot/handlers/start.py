# Telegram handler which sending welcome text

from aiogram import types, Router
from aiogram.filters import Command
from bot.conf import config_tg
from utils import keyboards
import random
from services.db.user_group import auto_add

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
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

    welcome_text = f"Привет, {message.from_user.first_name.capitalize()}! Я <b>BoostBot</b> 🚀\nНажми на кнопку ниже, чтобы увидеть что я могу"
    

    kb = keyboards.get_commands_kb()

    effect_id = None
    if config_tg.message_effects:
        try:
            effect_id = random.choice(config_tg.message_effects)
        except Exception: effect_id = None

    await message.answer(
        text=welcome_text,
        message_effect_id=effect_id,
        reply_markup=kb,
        parse_mode="HTML"
    )

    await auto_add(message.from_user.id)


@router.callback_query(lambda c: c.data == "go_back_commands")
async def back_to_start(callback: types.CallbackQuery):

    kb = keyboards.get_commands_kb()
    
    welcome_text = f"Привет, {callback.from_user.first_name.capitalize()}! Я <b>BoostBot</b> 🚀\nНажми на кнопку ниже, чтобы увидеть что я могу"
    await callback.message.edit_text(
        welcome_text,
        reply_markup=kb,
        parse_mode="HTML"
    )
    await callback.answer()