import asyncio

from aiogram import Bot, types, Router
from aiogram.filters import BaseFilter, StateFilter
from utils.command_list import get_command_list_text as get
from aiogram.enums import ChatAction

router = Router()

c_list = get().split("\n")

class IdontKnowFilter(BaseFilter):
    key = "idontknow"

    async def __call__(self, message: types.Message) -> bool:
        if message.text and message.text.strip().lower() not in c_list:
            return True
        return not not message.text

@router.message(IdontKnowFilter(), StateFilter(None))
async def idunno(message: types.Message):
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    await asyncio.sleep(0.5)
    await message.reply(
        "<b>Извините, я не понимаю эту команду</b>\n\n"
        "<i>Вот список доступных команд:</i>\n" + get(),
        parse_mode="HTML"
    )
