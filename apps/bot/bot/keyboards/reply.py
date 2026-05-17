"""ReplyKeyboardMarkup'lar — asosiy menyu va boshqa tezroq tugmalar."""
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu() -> ReplyKeyboardMarkup:
    """Foydalanuvchi tizimga kirgan paytdagi asosiy klaviatura.

    Telegram reply-keyboard 3 ustunda ko'p tugmalarni qulay ko'rsatadi.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📊 GPA"),
                KeyboardButton(text="🏆 Guruh"),
                KeyboardButton(text="🎓 Fakultet"),
            ],
            [
                KeyboardButton(text="📈 TOP"),
                KeyboardButton(text="⚠️ Risk"),
                KeyboardButton(text="📈 Trend"),
            ],
            [
                KeyboardButton(text="📝 Baholar"),
                KeyboardButton(text="📅 Davomat"),
                KeyboardButton(text="🎯 Maqsad"),
            ],
            [
                KeyboardButton(text="🗓 Jadval"),
                KeyboardButton(text="📚 Imtihonlar"),
                KeyboardButton(text="🏛 Fakultetlar"),
            ],
            [
                KeyboardButton(text="🔔 Xabarlar"),
                KeyboardButton(text="📞 Aloqa"),
                KeyboardButton(text="👤 Profil"),
            ],
            [
                KeyboardButton(text="⚙️ Sozlamalar"),
                KeyboardButton(text="📋 Menyu"),
                KeyboardButton(text="❓ Yordam"),
            ],
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
