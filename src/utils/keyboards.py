from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_commands_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Начать", callback_data="show_commands")]
    ])

def get_back_commands_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="go_back_commands")]
    ])

def get_back_commands_custom(callback_data:str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data=callback_data)]
    ])

def con_var_img_kb() -> InlineKeyboardMarkup:
    formats = [
        ("PNG", "convert_to_png"),
        ("JPEG", "convert_to_jpeg"),
        ("WEBP", "convert_to_webp")
    ]
    keyboard = [[InlineKeyboardButton(text=text, callback_data=data)] for text, data in formats]
    keyboard.append([InlineKeyboardButton(text="Назад", callback_data="back_commands_conv")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def text_conversion_kb() -> InlineKeyboardMarkup:
    formats = [
        ("PDF", "convert_to_pdf"),
        ("Word (DOCX)", "convert_to_docx")
    ]
    keyboard = [[InlineKeyboardButton(text=text, callback_data=data)] for text, data in formats]
    keyboard.append([InlineKeyboardButton(text="Назад", callback_data="back_commands_conv")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def main_conversion_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Конвертировать изображение", callback_data="convert_image")],
        [InlineKeyboardButton(text="Конвертировать текст", callback_data="convert_text")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def yes_no_group_want_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text='Да', callback_data="want_add_group")],
        [InlineKeyboardButton(text="Нет", callback_data="dont_want_add_group")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def watch_schedule_edit_group_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Смотреть расписание", callback_data="watch_schedule_btn")], 
        [InlineKeyboardButton(text="Изменить группу", callback_data="edit_group_btn")]
    ] 
    return InlineKeyboardMarkup(inline_keyboard=buttons)