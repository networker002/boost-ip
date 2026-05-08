import asyncio
from aiogram import Bot, Router, F, types
from aiogram.types import Message
from aiogram.filters import BaseFilter, StateFilter
from aiogram.enums import ChatAction
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, WebAppInfo

from utils.command_list import get_command_list_text as get

router = Router()
c_list = [cmd.strip().lower() for cmd in get().split("\n") if cmd.strip()]

builder = InlineKeyboardBuilder()
builder.row(InlineKeyboardButton(
        text="Открыть дневник", 
        web_app=WebAppInfo(url="https://networker002.github.io/webapp/")
    ))

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
    s_id = "CAACAgEAAxkDAAIC02n8kf4y4mOHy7Ve0F7Q_NsFCS7SAAJtCwACxZ3oRwVDI0xmpxilOwQ"
    if message.sticker.file_id != s_id:
        await message.react([types.ReactionTypeEmoji(emoji="👍")])
        await message.reply_sticker(s_id)
    elif message.sticker.file_id == s_id:
        await message.reply("Нет. Это мой стикер!\nЛучше посмотри расписание 👌", reply_markup=builder.as_markup())