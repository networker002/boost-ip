# Telegram handler which sening list of comands and inline btn

from aiogram import Router, types
from aiogram.filters import Command
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
    commands_list = "\n".join(get())
    text = f'''<a href="https://telegra.ph/BoostBot--Commands-02-22">BoostBot | Commands</a>
    Вот список команд, <b>который только пополняется!</b>
   {commands_list}'''

    await message.answer(text, parse_mode="HTML")


@router.callback_query(lambda c: c.data == "show_commands")
async def on_show_commands(callback: types.CallbackQuery):
    # await callback.message.answer_document(
    #     document=types.FSInputFile(path="src/shared/fr/list.html"),
    #     caption=f"Вот список моих комманд, <b>который только пополняется!</b>\n- {"\n- ".join(get())}",
    #     parse_mode="HTML",
    #     reply_markup=keyboards.get_back_commands_kb()
    # )
    commands_lst = "\n".join(get())
    await callback.message.edit_text(
        text=f'''<a href="https://telegra.ph/BoostBot--Commands-02-22">BoostBot | Commands</a>\nВот список команд, <b>который только пополняется!</b>
{commands_lst}''',
        parse_mode="HTML",
        reply_markup=keyboards.get_back_commands_kb()
    )
    await callback.answer()


