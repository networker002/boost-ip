from aiogram import types, F, Bot, Router
from aiogram.filters.chat_member_updated import MEMBER

router = Router()

@router.my_chat_member()
async def bot_added_to_group(event: types.ChatMemberUpdated):
    if event.new_chat_member.status == "administrator":
        await event.answer(f"<b>BoostBot</b> на месте!\nОбязуюсь помогать всем нуждающимся с расписанием и прочими проблемами\nКлянусь быть максимально полезным <tg-emoji emoji-id='5224535095167184791'>⚡️</tg-emoji>", parse_mode="HTML")
    elif event.new_chat_member.status == "member":
        await event.answer("Привет! Сделайте меня админом, чтобы я мог модерировать чат 💎")
