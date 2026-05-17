from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram import F
# from aiogram.filters import BaseFilter

router = Router()

# class ReplyFromBot(BaseFilter):
#     async def __call__(self, message: types.Message, bot: Bot) -> bool:
#         return message.reply_to_message.from_user.id == bot.id
    
@router.message(Command("pin"))
async def pin_message(message: types.Message, bot: Bot):
    if not message.reply_to_message:
        await message.answer("Пожалуйста, ответьте на сообщение, которое хотите закрепить.")
        return
    #print("Pinning message...")
    try:
        await bot.pin_chat_message(chat_id=message.chat.id, message_id=message.reply_to_message.message_id, request_timeout=10)
        # await message.chat.pin_message(message.reply_to_message.message_id)

    except Exception as e:
        await message.answer("Упс, не могу закрепить сообщение. Убедитесь, что я админ и попробуйте снова.")


@router.message(Command("unpin"))
async def unpin_message(message: types.Message, bot: Bot):
    if not message.reply_to_message:
        await message.answer("Пожалуйста, ответьте на сообщение, которое хотите открепить.")
        return
    #print("Unpinning message...")
    try:
        # await message.unpin()
        await bot.unpin_chat_message(chat_id=message.chat.id, message_id=message.reply_to_message.message_id, request_timeout=10)
        # await message.chat.unpin_message(message.reply_to_message.message_id)

    except Exception as e:
        await message.answer("Упс, не могу открепить сообщение. Убедитесь, что я админ и попробуйте снова.")

@router.message(F.text.contains("закреп"))
async def pin_message_text(message: types.Message, bot: Bot):
    if message.reply_to_message:
        try:
            await bot.pin_chat_message(chat_id=message.chat.id, message_id=message.reply_to_message.message_id, request_timeout=10)
        except Exception as e:
            await message.answer("Упс, не могу закрепить сообщение. Убедитесь, что я админ и попробуйте снова.")

    
@router.message(F.text.contains("откреп"))
async def unpin_message_text(message: types.Message, bot: Bot):
    if message.reply_to_message:
        try:
            await bot.unpin_chat_message(chat_id=message.chat.id, message_id=message.reply_to_message.message_id, request_timeout=10)
        except Exception as e:
            await message.answer("Упс, не могу открепить сообщение. Убедитесь, что я админ и попробуйте снова.")