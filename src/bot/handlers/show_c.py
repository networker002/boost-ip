# Telegram handler which sening list of comands and inline btn

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import LinkPreviewOptions
from utils.command_list import get_command_list_text as get
from utils import keyboards

router = Router()

@router.message(Command("commands"))
async def cmd_show_commands(message: types.Message):
    # await message.answer_document( 
    #     caption=f"Вот список моих комманд, <b>который только пополняется!</b>\n- {"\n- ".join(get())}",
    #     document=types.FSInputFile(path="src/shared/fr/list.html"), 
    #     parse_mode="HTML"
    # )
    commands_list = get()
    text = f'''<b>BoostBot | Commands\nВот список команд, который только пополняется!</b>
{commands_list}

<tg-emoji emoji-id="5767420838282267710">🎨</tg-emoji> Но лучше всего пользоваться нашим <a href="t.me/mietcbot/webapp">приложением</a>'''

    await message.answer(text, parse_mode="HTML", link_preview_options=LinkPreviewOptions(url="t.me/mietcbot/webapp", show_above_text=False))


@router.callback_query(F.data == "show_commands")
async def on_show_commands(callback: types.CallbackQuery):
    # await callback.message.answer_document(
    #     document=types.FSInputFile(path="src/shared/fr/list.html"),
    #     caption=f"Вот список моих комманд, <b>который только пополняется!</b>\n- {"\n- ".join(get())}",
    #     parse_mode="HTML",
    #     reply_markup=keyboards.get_back_commands_kb()
    # )
    commands_lst = get()
    await callback.message.edit_text(
        text=f'''<b>BoostBot | Commands\nВот список команд, который только пополняется!</b>
{commands_lst}

<tg-emoji emoji-id="5767420838282267710">🎨</tg-emoji> Но лучше всего пользоваться нашим <a href="t.me/mietcbot/webapp">приложением</a>''',
        parse_mode="HTML",
        reply_markup=keyboards.get_back_commands_kb(),
        link_preview_options=LinkPreviewOptions(url="t.me/mietcbot/webapp", show_above_text=False)
    )
    await callback.answer()


