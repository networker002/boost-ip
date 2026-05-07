import asyncio
from aiogram import Bot, Router, F
from aiogram.types import Message
from aiogram.filters import BaseFilter, StateFilter
from aiogram.enums import ChatAction

from utils.command_list import get_command_list_text as get

router = Router()
c_list = [cmd.strip().lower() for cmd in get().split("\n") if cmd.strip()]

class IdontKnowFilter(BaseFilter):
    
    async def __call__(self, message: Message) -> bool:
        return bool(message.text) and message.text.strip().lower() not in c_list

@router.message(IdontKnowFilter(), StateFilter(None))
async def idunno(message: Message, bot: Bot):
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    await asyncio.sleep(0.5)
    await message.reply(
        "<b>Извините, я не понимаю эту команду</b>\n\n"
        "<i>Вот список доступных команд:</i>\n" + get(),
        parse_mode="HTML"
    )

@router.message(F.sticker)
async def and_st(message: Message):
    await message.answer_sticker(sticker="CAACAgEAAxkBAAEDxAxp_FYHmnT8vA30q4yGskiSGiUkPQAC5ggAAjxi4Uc4BD6jxvlNxTsE")