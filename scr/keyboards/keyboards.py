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
