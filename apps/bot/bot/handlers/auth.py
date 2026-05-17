"""Login / logout flow — aiogram FSM bilan."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from loguru import logger

from ..keyboards.inline import confirm_logout
from ..keyboards.reply import cancel_menu, main_menu
from ..services.api_client import ApiError, api_client
from ..services.auth_store import auth_store
from ..states.auth_states import LoginStates
from ..utils.formatters import fmt_role, md_escape

router = Router(name="auth")


@router.message(Command("login"))
async def cmd_login(
    message: Message, state: FSMContext, token: str | None
) -> None:
    if token:
        await message.answer(
            "Siz allaqachon tizimga kirgansiz. Chiqish uchun /logout"
        )
        return
    await state.set_state(LoginStates.waiting_username)
    await message.answer(
        "🔐 Tizimga kirish\n\nUsername'ni yuboring:",
        reply_markup=cancel_menu(),
    )


@router.message(F.text == "❌ Bekor qilish")
async def cancel_anywhere(message: Message, state: FSMContext) -> None:
    if await state.get_state() is None:
        return
    await state.clear()
    await message.answer(
        "Bekor qilindi", reply_markup=ReplyKeyboardRemove()
    )


@router.message(LoginStates.waiting_username, F.text)
async def receive_username(
    message: Message, state: FSMContext
) -> None:
    username = (message.text or "").strip()
    if len(username) < 3:
        await message.answer("Username juda qisqa. Qayta urinib ko'ring:")
        return
    await state.update_data(username=username)
    await state.set_state(LoginStates.waiting_password)
    await message.answer(
        "🔑 Parolni yuboring:\n\n"
        "_Eslatma: xavfsizlik uchun parolingizni yuborgach,"
        " uni Telegramdan o'chirishingizni tavsiya qilamiz._",
        parse_mode="Markdown",
    )


@router.message(LoginStates.waiting_password, F.text)
async def receive_password(
    message: Message, state: FSMContext
) -> None:
    data = await state.get_data()
    username = data.get("username", "")
    password = message.text or ""

    # Foydalanuvchi parolini chatdan o'chirishga harakat (Telegram limitlari ichida)
    try:
        await message.delete()
    except Exception:
        pass

    try:
        result = await api_client.login(username, password)
    except ApiError as e:
        logger.warning("Login xato: chat={} err={}", message.chat.id, e)
        await message.answer(
            f"❌ Kirish amalga oshmadi: {e}\n\nQayta urinish: /login",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.clear()
        return

    access = result.get("access_token")
    if not access:
        await message.answer(
            "❌ Token olinmadi. Backend bilan bog'lanishda muammo.",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.clear()
        return

    # Foydalanuvchi ma'lumotlarini olish
    try:
        user = await api_client.me(access)
    except ApiError:
        user = result.get("user") or {}

    await auth_store.save(
        message.chat.id,
        access_token=access,
        refresh_token=result.get("refresh_token"),
        user=user,
    )
    await state.clear()

    name = md_escape(user.get("full_name") or username)
    role = md_escape(fmt_role(user.get("role", "")))
    await message.answer(
        f"✅ *Xush kelibsiz, {name}\\!*\n\nRolingiz: _{role}_",
        parse_mode="MarkdownV2",
        reply_markup=main_menu(),
    )


@router.message(Command("logout"))
async def cmd_logout(message: Message, token: str | None) -> None:
    if not token:
        await message.answer("Siz tizimga kirmagansiz")
        return
    await message.answer(
        "Chindan ham chiqishni xohlaysizmi?", reply_markup=confirm_logout()
    )


@router.callback_query(F.data == "logout:yes")
async def logout_confirm(callback: CallbackQuery) -> None:
    if callback.message:
        await auth_store.clear(callback.from_user.id)
        await callback.message.edit_text("👋 Tizimdan chiqdingiz")
    await callback.answer()


@router.callback_query(F.data == "logout:no")
async def logout_cancel(callback: CallbackQuery) -> None:
    if callback.message:
        await callback.message.edit_text("Bekor qilindi")
    await callback.answer()
