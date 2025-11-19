from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from scr.FSM.states import RegistrationStates, AdminStates
from scr.keyboards.keyboards import (
    get_phone_keyboard, 
    get_role_keyboard, 
    get_cancel_keyboard, 
    remove_keyboard,
    get_main_menu_keyboard,
    get_admin_keyboard
)
from scr.database.__init__ import get_all_teams, get_all_users, get_captains, delete_user, get_users_by_team_id, get_user

from config import ADMIN_ID

router = Router()

@router.message(Command("admin"))
async def cmd_menu(message: Message):
    user = await get_user(message.from_user.id)
    print(await get_users_by_team_id("584647"))
    if (user['telegram_id'] != int(ADMIN_ID)):
        await message.answer(
            "❗️ У вас немає доступу до цієї команди."
        )
        return
    
    await message.answer(
        f"📋 Головне меню\n\n"
        f"👤 {user['full_name']}\n"
        f"👷 Адміністратор",
        reply_markup=get_admin_keyboard()
    )

@router.callback_query(F.data == "get_all_users")
async def show_all_users(callback: CallbackQuery):
    users_list = await get_all_users()

    if not users_list:
        await callback.message.answer("Список користувачів порожній.")
        await callback.answer()
        return

    text = "📋 *Список всіх користувачів:*\n\n"
    for i, user in enumerate(users_list, 1):
        text += f"{i}. {user['full_name']} (ID: `{user['telegram_id']}`) {("No username", f"@{user['username']}")[user['username'] != ""]}\n"

    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "get_all_teams")
async def show_all_teams(callback: CallbackQuery):
    teams_list = await get_all_teams()

    if not teams_list:
        await callback.message.answer("Список команд порожній.")
        await callback.answer()
        return
    
    text = "📋 *Список всіх команд:*\n\n"
    for i, team in enumerate(teams_list, 1):
        text += f"{i}. {team['name']} (Code: `{team['code']}`) Members: {team['max_members']}\n"

    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "get_all_captains")
async def show_all_users(callback: CallbackQuery):
    caps_list = await get_captains()

    if not caps_list:
        await callback.message.answer("Список капітанів порожній.")
        await callback.answer()
        return

    text = "📋 *Список всіх капітанів:*\n\n"
    for i, cap in enumerate(caps_list, 1):
        text += f"{i}. {cap['full_name']} (ID: `{cap['telegram_id']}`) {("No username", f"@{cap['username']}")[cap['username'] != ""]}\n"

    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "delete_user")
async def ask_user_id_for_delete(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🔢 Введіть *telegram_id* користувача, якого хочете видалити:", parse_mode="Markdown")
    await state.set_state(AdminStates.waiting_for_delete_user_id)
    await callback.answer()


@router.message(AdminStates.waiting_for_delete_user_id)
async def delete_user_by_id(message: Message, state: FSMContext):
    try:
        telegram_id = int(message.text.strip())
    except ValueError:
        await message.answer("❗️ ID має бути числом. Спробуйте ще раз.")
        return

    result = await delete_user(telegram_id)

    if result:
        await message.answer(f"🗑 Користувача з ID `{telegram_id}` успішно видалено.", parse_mode="Markdown")
    else:
        await message.answer(f"❌ Не вдалося знайти або видалити користувача з ID `{telegram_id}`.", parse_mode="Markdown")

    await state.clear()


def register_handlers(dp):
    dp.include_router(router)