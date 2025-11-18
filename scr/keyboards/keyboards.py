from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_phone_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.button(text="📱 Надіслати номер телефону", request_contact=True)
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def get_role_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="👑 Капітан команди", callback_data="role_captain")
    kb.button(text="👤 Учасник команди", callback_data="role_member")
    kb.adjust(1)
    return kb.as_markup()


def get_cancel_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.button(text="❌ Скасувати")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def remove_keyboard():
    from aiogram.types import ReplyKeyboardRemove
    return ReplyKeyboardRemove()


def get_main_menu_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="📜 Регламент", url="https://docs.google.com/document/d/1VaSC_Gc7i1jSsX333Q1VY7-NllevVRT1bss2i6sLpYA/edit?usp=sharing")
    kb.button(text="📝 Технічне завдання", url="https://docs.google.com/document/d/1M0xUlyMQSGlgt7gqPykxgIM4kKgpbqqYEt2k6sWaDHg/edit?usp=sharing")
    kb.adjust(1)
    return kb.as_markup()


def get_captain_menu_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="📜 Регламент", url="https://docs.google.com/document/d/1VaSC_Gc7i1jSsX333Q1VY7-NllevVRT1bss2i6sLpYA/edit?usp=sharing")
    kb.button(text="📝 Технічне завдання", url="https://docs.google.com/document/d/1M0xUlyMQSGlgt7gqPykxgIM4kKgpbqqYEt2k6sWaDHg/edit?usp=sharing")
    kb.button(text="⚙️ Управління командою", callback_data="manage_team")
    kb.adjust(1)
    return kb.as_markup()


def get_team_management_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="✏️ Змінити назву команди", callback_data="edit_team_name")
    kb.button(text="👥 Змінити кількість учасників", callback_data="edit_team_size")
    kb.button(text="👤 Видалити учасника", callback_data="remove_member")
    kb.button(text="📊 Інформація про команду", callback_data="team_info")
    kb.button(text="🔙 Назад", callback_data="back_to_menu")
    kb.adjust(1)
    return kb.as_markup()
