"""Inline menyu tugmalari uchun callback handlerlar."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from ..keyboards.inline import main_menu_inline, settings_inline
from . import data as data_handlers
from . import tz_commands as tz
from .start import HELP

router = Router(name="menu_cb")


@router.callback_query(F.data == "menu:home")
async def home(callback: CallbackQuery, token: str | None) -> None:
    if not token:
        await callback.answer("Sessiya tugagan — /login", show_alert=True)
        return
    if callback.message:
        await callback.message.edit_text(
            "📋 *Asosiy menyu*\n\nKerakli bo'limni tanlang:",
            reply_markup=main_menu_inline(),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data == "menu:settings")
async def settings(callback: CallbackQuery, token: str | None) -> None:
    if not token:
        await callback.answer("Sessiya tugagan — /login", show_alert=True)
        return
    if callback.message:
        await callback.message.edit_text(
            "⚙️ *Sozlamalar*",
            reply_markup=settings_inline(),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data == "menu:help")
async def help_menu(callback: CallbackQuery) -> None:
    if callback.message:
        await callback.message.answer(HELP, parse_mode="Markdown")
    await callback.answer()


# Boshqa tugmalar — handler komandasini chaqiramiz (message orqali javob beradi).
_DISPATCH = {
    "menu:gpa":           data_handlers.cmd_gpa,
    "menu:grades":        data_handlers.cmd_grades,
    "menu:schedule":      data_handlers.cmd_schedule,
    "menu:notifications": data_handlers.cmd_notifications,
    "menu:profile":       data_handlers.cmd_profile,
    "menu:rank":          data_handlers.cmd_rank,
    "menu:rank_faculty":  data_handlers.cmd_rank_faculty,
    "menu:top":           tz.cmd_top,
    "menu:davomat":       tz.cmd_davomat,
    "menu:imtihon":       tz.cmd_imtihon,
    "menu:aloqa":         tz.cmd_aloqa,
    "menu:notify_settings": data_handlers.cmd_notify_settings,
}


@router.callback_query(F.data.startswith("menu:"))
async def menu_dispatch(
    callback: CallbackQuery, token: str | None, user: dict | None
) -> None:
    handler = _DISPATCH.get(callback.data or "")
    if handler is None or callback.message is None:
        await callback.answer()
        return
    # /profile handler `user` ham talab qiladi
    if callback.data == "menu:profile":
        await handler(callback.message, token, user)
    else:
        await handler(callback.message, token)
    await callback.answer()
