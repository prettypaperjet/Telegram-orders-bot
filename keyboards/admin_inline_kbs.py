from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicons.lexicon import LEXICON_ADM


def start_kb_adm() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton(text=LEXICON_ADM["show_orders_adm"], callback_data="/show_orders_adm")],
                [InlineKeyboardButton(text=LEXICON_ADM["db"], callback_data="/manage_db")],
                [InlineKeyboardButton(text=LEXICON_ADM["help_adm"], callback_data="/help")]
                ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard, resize_keyboard=True)


def back_kb_adm() -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]] = [[InlineKeyboardButton(text=LEXICON_ADM["back_kb_adm"], callback_data="back")]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def back_db_kb() -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]] = [[InlineKeyboardButton(text=LEXICON_ADM["back_kb_adm"], callback_data="back_db")]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def topic_kb_db(topics: list) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()

    for keyword in topics:
        kb_builder.add(InlineKeyboardButton(
            text=keyword,
            callback_data=keyword)
        )
    kb_builder.adjust(2)
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON_ADM["back_kb_adm"],
            callback_data="back_db"
        )
    )
    return kb_builder.as_markup()


def manage_db_kb() -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=LEXICON_ADM["add_photo_db"], callback_data="/add_photo_db")],
        [InlineKeyboardButton(text=LEXICON_ADM["delete_photo_db"], callback_data="/delete_photo_db")],
        [InlineKeyboardButton(text=LEXICON_ADM["show_photo_db"], callback_data="/show_photo_db")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def orders_kb_comm(users: dict) -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]] = [[InlineKeyboardButton(text=f"{data['name']} (id: {id_user})",
                                                                        url=f"https://t.me/{data['username']}",
                                                                        callback_data=f"order_{id_user}")]
                                                  for id_user, data in users.items()
                                                  ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def orders_kb_choose(users: dict) -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]] = [[InlineKeyboardButton(text=f"{data['name']} (id: {id_user})",
                                                                        callback_data=f"order_{id_user}")]
                                                  for id_user, data in users.items()
                                                  ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def reply_new_order() -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]] = [[InlineKeyboardButton(text=LEXICON_ADM["reply_new_order"],
                                                                        callback_data="/show_orders_adm")]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def choose_change_ord() -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]] = [[InlineKeyboardButton(text=LEXICON_ADM["change_confirm_order"],
                                                                        callback_data="/yes")],
                                                  [InlineKeyboardButton(text=LEXICON_ADM["confirm_order"],
                                                                        callback_data="/no")]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def choose_change_data() -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]] = [[InlineKeyboardButton(text=LEXICON_ADM["change_name_bt"],
                                                                        callback_data="change_name")],
                                                  [InlineKeyboardButton(text=LEXICON_ADM["change_descr_bt"],
                                                                        callback_data="change_descr")],
                                                  [InlineKeyboardButton(text=LEXICON_ADM["change_date_bt"],
                                                                        callback_data="change_date")]
                                                  ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

