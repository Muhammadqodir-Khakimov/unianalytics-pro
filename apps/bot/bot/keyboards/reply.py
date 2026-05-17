"""ReplyKeyboardMarkup'lar — asosiy menyu va boshqa tezroq tugmalar."""
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu() -> ReplyKeyboardMarkup:
    """Foydalanuvchi tizimga kirgan paytdagi asosiy klaviatura."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 GPA"), KeyboardButton(text="📝 Baholar")],
            [KeyboardButton(text="📅 Jadval"),
             KeyboardButton(text="🔔 Xabarlar")],
            [KeyboardButton(text="👤 Profil"),
             KeyboardButton(text="❓ Yordam")],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def cancel_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
