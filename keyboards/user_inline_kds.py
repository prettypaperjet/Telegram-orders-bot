
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicons.lexicon import LEXICON


def start_kb(*buttons: str) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(*[InlineKeyboardButton(
        text=LEXICON[button] if button in LEXICON else button,
        callback_data="/"+button) for button in buttons],
        width=1
    )
    return kb_builder.as_markup()


def back_kb() -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]] = [[InlineKeyboardButton(text=LEXICON["back"], callback_data="/back")]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def topic_kb(topics: list) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()

    for keyword in topics:
        kb_builder.add(InlineKeyboardButton(
            text=keyword,
            callback_data=keyword)
        )
    kb_builder.adjust(2)
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON["custom"],
            callback_data="/custom"
        )
    )
    return kb_builder.as_markup()


'''
def answer_descr_kb() -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]] = [[InlineKeyboardButton(text="Написать описание", callback_data="/yes")],
                                                  [InlineKeyboardButton(text="Продолжить без описания", callback_data="/no")]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
'''
