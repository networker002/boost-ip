from aiogram import types, Router
from aiogram.filters import Command
from services.db.user_group import check_user_group
router = Router()

@router.message(Command("profile"))
async def show_profile(message: types.Message):
    username = message.from_user.username
    id_ = message.from_user.id
    c = await check_user_group(id_)
    if c:
        group = c["group_name"]
    else: group = "Не указана"
    subscribe = "Пока в разработке"

    text = f"""<b>Твой профиль</b>

    <b>┏Имя пользователя: </b>{("@"+username) if username else "Отсутствует"}
    <b>┣Айди аккаунта: </b>{id_}
    <b>┣Группа: </b>{group}
    <b>┖Подписка: </b>{subscribe}"""
    await message.answer(text, parse_mode="HTML")
