"""Inline klaviaturalar — sahifalash va boshqa interaktiv tugmalar."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def grades_pagination(page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Baholar ro'yxati uchun sahifalash tugmalari."""
    buttons: list[InlineKeyboardButton] = []
    if page > 1:
        buttons.append(InlineKeyboardButton(
            text="« Oldingi", callback_data=f"grades:{page - 1}",
        ))
    buttons.append(InlineKeyboardButton(
        text=f"{page} / {total_pages}", callback_data="noop",
    ))
    if page < total_pages:
        buttons.append(InlineKeyboardButton(
            text="Keyingi »", callback_data=f"grades:{page + 1}",
        ))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def confirm_logout() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha, chiqaman",
                                 callback_data="logout:yes"),
            InlineKeyboardButton(text="❌ Bekor", callback_data="logout:no"),
        ],
    ])


def main_menu_inline() -> InlineKeyboardMarkup:
    """Rich inline asosiy menyu — barcha buyruqlar bitta klaviaturada."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 GPA", callback_data="menu:gpa"),
            InlineKeyboardButton(text="🏆 Guruh", callback_data="menu:rank"),
            InlineKeyboardButton(text="🎓 Fakultet", callback_data="menu:rank_faculty"),
        ],
        [
            InlineKeyboardButton(text="📈 TOP talabalar", callback_data="menu:top"),
            InlineKeyboardButton(text="⚠️ Risk guruhi", callback_data="menu:xavf"),
        ],
        [
            InlineKeyboardButton(text="📝 Baholar", callback_data="menu:grades"),
            InlineKeyboardButton(text="📅 Davomat", callback_data="menu:davomat"),
            InlineKeyboardButton(text="📈 Trend", callback_data="menu:trend"),
        ],
        [
            InlineKeyboardButton(text="🗓 Jadval", callback_data="menu:schedule"),
            InlineKeyboardButton(text="📚 Imtihonlar", callback_data="menu:imtihon"),
        ],
        [
            InlineKeyboardButton(text="🏛 Fakultetlar", callback_data="menu:top_fakultet"),
            InlineKeyboardButton(text="🎯 Maqsad", callback_data="menu:maqsad"),
        ],
        [
            InlineKeyboardButton(text="🔔 Xabarlar", callback_data="menu:notifications"),
            InlineKeyboardButton(text="👤 Profil", callback_data="menu:profile"),
        ],
        [
            InlineKeyboardButton(text="📞 Aloqa", callback_data="menu:aloqa"),
            InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="menu:notify_settings"),
        ],
        [
            InlineKeyboardButton(text="🔄 Yangilash", callback_data="menu:home"),
            InlineKeyboardButton(text="❓ Yordam", callback_data="menu:help"),
        ],
    ])


def settings_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔔 Bildirishnomalar",
                              callback_data="set:notify")],
        [InlineKeyboardButton(text="🚪 Chiqish",
                              callback_data="set:logout")],
        [InlineKeyboardButton(text="« Orqaga",
                              callback_data="menu:home")],
    ])
