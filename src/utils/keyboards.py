from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
import random

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

def profile_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Посмотреть расписание", web_app=WebAppInfo(url="https://networker002.github.io/webapp/"))], 
        [InlineKeyboardButton(text="Изменить группу", callback_data="edit_group_btn")]
    ] 
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def swipe_schedule_kb(prev_week:str, next_week:str, prev_data: str = "prev_week", next_data: str = "next_week") -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    t = ["📩",
        "📥",
        "🗓",
        "📚",
        "📎",
        "📝"]
    tr = random.choice(t)
    if not prev_week:
        builder.add(
        InlineKeyboardButton(text=next_week+" ➡️", callback_data=next_data)
        )
        builder.add(
            InlineKeyboardButton(text=tr+" Скачать расписание", callback_data="download_schedule")
        )
        builder.adjust(1, 1)
    elif not next_week:
        builder.add(
            InlineKeyboardButton(text="⬅️ "+prev_week, callback_data=prev_data)
        )
        builder.add(
            InlineKeyboardButton(text=tr+" Скачать расписание", callback_data="download_schedule")
        )
        builder.adjust(1, 1)
    else:
        builder.add(
            InlineKeyboardButton(text="⬅️ "+prev_week, callback_data=prev_data)
        )
        
        builder.add(
        InlineKeyboardButton(text=next_week+" ➡️", callback_data=next_data)
        )
        
        builder.add(
            InlineKeyboardButton(text=tr+" Скачать расписание", callback_data="download_schedule")
        )
        builder.adjust(2, 1)

    return builder.as_markup()

def dwn_days_kb(schedule: list, selected_days: list = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if selected_days is None:
        selected_days = []

    if schedule:
        for week_index, week in enumerate(schedule):
            for day in week:
                day_str = str(day)
                is_selected = day_str in selected_days
                text = f"✅" if is_selected else day_str[:2]
                
                builder.add(InlineKeyboardButton(
                    text=text, 
                    callback_data=f"add_{day_str}")
                )
            
            builder.add(InlineKeyboardButton(
                text="ВСЕ", 
                callback_data=f"all_{week_index}")
            )
            
    builder.add(InlineKeyboardButton(text="Применить", callback_data="download_new_sc"))
    builder.add(InlineKeyboardButton(text="Отменить", callback_data="cancel_add"))
    builder.adjust(*(7 for _ in range(len(schedule))), 1, 1)
        
    return builder.as_markup()

def go_or_back_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(text="Экспорт HTML", callback_data="schedule_html"))
    builder.add(InlineKeyboardButton(text="Экспорт EXCEL", callback_data="schedule_exel"))
    builder.add(InlineKeyboardButton(text="Экспорт TXT", callback_data="schedule_txt"))
    builder.add(InlineKeyboardButton(text="Экспорт картинкой", callback_data="schedule_img"))
    builder.add(InlineKeyboardButton(text="Назад", callback_data="download_schedule"))
    
    builder.adjust(1,1,1,1)
    
    return builder.as_markup()

def styles_choise_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(text="🟢 Зеленая", callback_data="html_green"))
    builder.add(InlineKeyboardButton(text="🔵 Синяя", callback_data="html_blue"))
    builder.add(InlineKeyboardButton(text="🟠 Оранжевая", callback_data="html_orange"))
    builder.add(InlineKeyboardButton(text="⚫ Темная", callback_data="html_dark"))
    builder.add(InlineKeyboardButton(text="🟣 Фиолетовая", callback_data="html_purple"))
    
    builder.adjust(2)
    
    return builder.as_markup()

def want_to_repeat_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(text="Повторить", callback_data="want_to_repeat"))
    
    builder.adjust(1)
    
    return builder.as_markup()