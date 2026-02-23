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
    subscribe = "Пока в разработке"

    await message.reply(
        f"<b>Твой профиль</b>\n\n<b>┏Имя пользователя: </b>{("@"+username) if not None else "Отсутствует"}\n<b>┣Айди аккаунта: </b>{id_}\n<b>┣Группа: </b>{group}\n<b>┖Подписка: </b>{subscribe}",
        parse_mode="HTML"
    )

