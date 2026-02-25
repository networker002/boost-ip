from aiogram import Router, types, Bot
from aiogram.filters import Command
from services.convert import Converter
from utils import keyboards
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import F
import io
from aiogram.types import Message
from aiogram.filters import BaseFilter
from services import html_do

router = Router()

class ReplyFromBot(BaseFilter):
    key = "reply_to_bot"
    async def __call__(self, message: Message, bot: Bot) -> bool:
        if not message.reply_to_message:
            return False
        return message.reply_to_message.from_user.id == bot.id
    

class OrderConvert(StatesGroup):
    choosing_category = State()
    image_state = State()
    text_input_state = State()
    text_format_state = State()



@router.message(Command("convert"), ReplyFromBot())
async def test(message: Message):
    answered_msg = message.reply_to_message.text

    if answered_msg.startswith("Вот твое расписание"):
        res = html_do.HTMLdocument().generate_html(answered_msg)
        path = io.BytesIO()
        path.write(res.encode("utf-8"))
        path.seek(0)
        await message.answer_document(
            document=types.BufferedInputFile(
                path.getvalue(),
                filename="schedule.html"
            ),
            caption="Расписание"
        )

@router.message(Command("convert"))
async def reg_conv(message: types.Message, state: FSMContext):
    # if message.text.strip() == "/convert schedule":
    #     await message.answer("Конвертирую расписание!")

        
    await message.answer(
        "Выберите тип конвертации:",
        reply_markup=keyboards.main_conversion_kb()
    )
    await state.set_state(OrderConvert.choosing_category)

@router.callback_query(F.data == "convert_image")
async def start_image_conversion(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Отправьте изображение для конвертации:",
        reply_markup=keyboards.get_back_commands_custom("back_commands_conv")
    )
    await state.set_state(OrderConvert.image_state)
    await callback.answer()

@router.callback_query(F.data == "convert_text")
async def start_text_conversion(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Введите текст для конвертации:",
        reply_markup=keyboards.get_back_commands_custom("back_commands_conv")
    )
    await state.set_state(OrderConvert.text_input_state)
    await callback.answer()

@router.message(OrderConvert.image_state, F.document)
async def handle_image_document(message: types.Message, state: FSMContext):
    doc = message.document
    mime_type = doc.mime_type.lower() if doc.mime_type else ""

    if mime_type.startswith("image/"):
        await state.update_data(
            document_id=doc.file_id,
            original_filename=doc.file_name
        )

        kb = keyboards.con_var_img_kb()
        await message.answer(
            "Выберите формат для конвертации изображения:",
            reply_markup=kb
        )
    else:
        await message.answer("Это не изображение. Отправьте файл изображения (PNG, JPEG, WEBP).")

@router.message(OrderConvert.text_input_state, F.text)
async def handle_text_input(message: types.Message, state: FSMContext):
    text = message.text

    await state.update_data(input_text=text)

    kb = keyboards.text_conversion_kb()
    await message.answer(
        "Выберите формат для конвертации текста:",
        reply_markup=kb
    )
    await state.set_state(OrderConvert.text_format_state)


@router.callback_query(
    OrderConvert.image_state,
    F.data.in_(["convert_to_png", "convert_to_jpeg", "convert_to_webp"])
)
async def convert_image_format(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer(text="Конвертация запущена. Ожидайте до 3 мин")

    data = await state.get_data()
    document_id = data.get("document_id")
    original_filename = data.get("original_filename", "image")

    format_map = {
        "convert_to_png": "PNG",
        "convert_to_jpeg": "JPEG",
        "convert_to_webp": "WEBP"
    }
    target_format = format_map.get(callback.data)

    if not target_format:
        await callback.answer("Неизвестный формат конвертации")
        return
    
    try:
        file = await bot.get_file(document_id)
        file_path = file.file_path
        image_bytes = io.BytesIO()
        await bot.download_file(file_path, image_bytes)

        converted_image = Converter.img_conv(image_bytes, target_format)

        base_name = original_filename.rsplit('.', 1)[0] if '.' in original_filename else original_filename
        new_filename = f"{base_name}.{target_format.lower()}"

        await callback.message.answer_document(
            document=types.BufferedInputFile(
                converted_image.getvalue(),
                filename=new_filename
            ),
            caption=f"Конвертировано в {target_format}"
        )

        await state.clear()

    except Exception as e:
        await callback.message.answer(f"Ошибка конвертации: {str(e)}")
        await state.clear()


@router.callback_query(
    OrderConvert.text_format_state,
    F.data.in_(["convert_to_pdf", "convert_to_docx"])
)
async def convert_text_format(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer(text="Конвертация запущена. Ожидайте")

    data = await state.get_data()
    text = data.get("input_text")

    if text.startwith("Вот твое расписание"):
        await callback.message.answer("Похоже, вы собираетесь конвертировать расписание. ")

    format_map = {
        "convert_to_pdf": ("PDF", "pdf"),
        "convert_to_docx": ("Word (DOCX)", "docx")
    }
    display_name, format_type = format_map.get(callback.data, ("Unknown", "txt"))

    try:
        if format_type == "pdf":
            converted_file = Converter.text_to_pdf(text)
            filename = "converted_text.pdf"
        else:
            converted_file = Converter.text_to_docx(text)
            filename = "converted_text.docx"

        await callback.message.answer_document(
            document=types.BufferedInputFile(
                converted_file.getvalue(),
                filename=filename
            ),
            caption=f"Текст конвертирован в {display_name}"
        )

        await state.clear()

    except Exception as e:
        await callback.message.answer(f"Ошибка конвертации текста: {str(e)}")
        await state.clear()


@router.callback_query(F.data == "back_commands_conv")
async def go_back_f(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Выберите тип конвертации:",
        reply_markup=keyboards.main_conversion_kb()
    )
    await callback.answer()
    await state.set_state(OrderConvert.choosing_category)

@router.message(OrderConvert.image_state)
async def invalid_image_input(message: types.Message):
    await message.answer(
        "Пожалуйста, отправьте файл изображения (PNG, JPEG, WEBP)",
        reply_markup=keyboards.get_back_commands_custom("back_commands_conv")
    )


@router.message(OrderConvert.text_input_state)
async def invalid_text_input(message: types.Message):
    await message.answer(
        "Пожалуйста, введите текст для конвертации",
        reply_markup=keyboards.get_back_commands_custom("back_commands_conv")
    )

