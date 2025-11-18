from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from scr.FSM.states import TeamManagementStates
from scr.keyboards.keyboards import (
    get_team_management_keyboard,
    get_captain_menu_keyboard,
    get_cancel_keyboard,
    remove_keyboard
)
from scr.database.__init__ import (
    get_user,
    get_team_by_captain_id,
    get_team_members_ids,
    update_team_info,
    remove_member_from_team,
    get_user_by_telegram_id
)

router = Router()


@router.callback_query(F.data == "manage_team")
async def show_team_management(callback: CallbackQuery):
    await callback.answer()
    
    user = await get_user(callback.from_user.id)
    if not user or not user.get('is_captain'):
        await callback.message.answer("❌ Ця функція доступна тільки капітанам команд")
        return
    
    team = await get_team_by_captain_id(callback.from_user.id)
    if not team:
        await callback.message.answer("❌ Ви не є капітаном жодної команди")
        return
    
    await callback.message.edit_text(
        "⚙️ Управління командою\n\n"
        "Оберіть дію:",
        reply_markup=get_team_management_keyboard()
    )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    await callback.answer()
    
    user = await get_user(callback.from_user.id)
    
    await callback.message.edit_text(
        f"📋 Головне меню\n\n"
        f"👤 {user['full_name']}\n"
        f"{'👑 Капітан команди' if user.get('is_captain') else '👤 Учасник команди'}",
        reply_markup=get_captain_menu_keyboard() if user.get('is_captain') else None
    )


@router.callback_query(F.data == "team_info")
async def show_team_info(callback: CallbackQuery):
    await callback.answer()
    
    team = await get_team_by_captain_id(callback.from_user.id)
    if not team:
        await callback.message.answer("❌ Команду не знайдено")
        return
    
    members_ids = team.get('members_telegram_ids', [])
    members_count = len(members_ids)
    
    members_text = ""
    for i, member_id in enumerate(members_ids, 1):
        user = await get_user_by_telegram_id(member_id)
        if user:
            role = "👑 Капітан" if user.get('is_captain') else "👤 Учасник"
            username = f"@{user.get('username')}" if user.get('username') else "немає username"
            members_text += f"{i}. {user['full_name']} ({username}) - {role}\n"
    
    await callback.message.edit_text(
        f"📊 Інформація про команду\n\n"
        f"🎯 Назва: {team['name']}\n"
        f"🔢 Унікальний номер: {team['unique_number']}\n"
        f"🔑 Код: {team['code']}\n"
        f"👥 Учасників: {members_count}/{team['max_members']}\n\n"
        f"Список учасників:\n{members_text}",
        reply_markup=get_team_management_keyboard()
    )


@router.callback_query(F.data == "edit_team_name")
async def start_edit_team_name(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    await callback.message.answer(
        "✏️ Введіть нову назву команди:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(TeamManagementStates.waiting_for_new_team_name)


@router.message(TeamManagementStates.waiting_for_new_team_name, F.text == "❌ Скасувати")
async def cancel_edit_team_name(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Зміну назви скасовано",
        reply_markup=remove_keyboard()
    )


@router.message(TeamManagementStates.waiting_for_new_team_name)
async def process_new_team_name(message: Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 3:
        await message.answer("❗️ Назва команди має містити мінімум 3 символи")
        return
    
    new_name = message.text.strip()
    team = await get_team_by_captain_id(message.from_user.id)
    
    if not team:
        await message.answer("❌ Команду не знайдено")
        await state.clear()
        return
    
    team_id = str(team['_id'])
    success = await update_team_info(team_id, {'name': new_name})
    
    if success:
        await message.answer(
            f"✅ Назву команди змінено на '{new_name}'",
            reply_markup=remove_keyboard()
        )
    else:
        await message.answer("❌ Помилка при зміні назви команди")
    
    await state.clear()


@router.callback_query(F.data == "edit_team_size")
async def start_edit_team_size(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    team = await get_team_by_captain_id(callback.from_user.id)
    current_members = len(team.get('members_telegram_ids', []))
    
    await callback.message.answer(
        f"👥 Введіть нову кількість учасників (від {current_members} до 6):\n\n"
        f"⚠️ Поточна кількість учасників: {current_members}",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(TeamManagementStates.waiting_for_new_max_members)


@router.message(TeamManagementStates.waiting_for_new_max_members, F.text == "❌ Скасувати")
async def cancel_edit_team_size(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Зміну кількості скасовано",
        reply_markup=remove_keyboard()
    )


@router.message(TeamManagementStates.waiting_for_new_max_members)
async def process_new_max_members(message: Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer("❗️ Введіть число від 1 до 6")
        return
    
    new_max = int(message.text)
    team = await get_team_by_captain_id(message.from_user.id)
    
    if not team:
        await message.answer("❌ Команду не знайдено")
        await state.clear()
        return
    
    current_members = len(team.get('members_telegram_ids', []))
    
    if new_max < current_members:
        await message.answer(
            f"❌ Не можна встановити кількість меншу за поточну кількість учасників ({current_members})"
        )
        return
    
    if new_max < 1 or new_max > 6:
        await message.answer("❗️ Кількість має бути від 1 до 6")
        return
    
    team_id = str(team['_id'])
    success = await update_team_info(team_id, {'max_members': new_max})
    
    if success:
        await message.answer(
            f"✅ Максимальну кількість учасників змінено на {new_max}",
            reply_markup=remove_keyboard()
        )
    else:
        await message.answer("❌ Помилка при зміні кількості учасників")
    
    await state.clear()


@router.callback_query(F.data == "remove_member")
async def start_remove_member(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    team = await get_team_by_captain_id(callback.from_user.id)
    if not team:
        await callback.message.answer("❌ Команду не знайдено")
        return
    
    members_ids = team.get('members_telegram_ids', [])
    
    if len(members_ids) <= 1:
        await callback.message.answer("❌ У команді немає учасників для видалення (тільки капітан)")
        return
    
    members_text = ""
    for i, member_id in enumerate(members_ids, 1):
        if member_id == callback.from_user.id:
            continue
        user = await get_user_by_telegram_id(member_id)
        if user:
            username = f"@{user.get('username')}" if user.get('username') else "немає username"
            members_text += f"{i}. {user['full_name']} ({username}) - ID: {member_id}\n"
    
    await callback.message.answer(
        f"👤 Виберіть учасника для видалення:\n\n{members_text}\n"
        f"Введіть Telegram ID учасника:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(TeamManagementStates.waiting_for_member_to_remove)


@router.message(TeamManagementStates.waiting_for_member_to_remove, F.text == "❌ Скасувати")
async def cancel_remove_member(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Видалення скасовано",
        reply_markup=remove_keyboard()
    )


@router.message(TeamManagementStates.waiting_for_member_to_remove)
async def process_remove_member(message: Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer("❗️ Введіть коректний Telegram ID (число)")
        return
    
    member_id = int(message.text)
    team = await get_team_by_captain_id(message.from_user.id)
    
    if not team:
        await message.answer("❌ Команду не знайдено")
        await state.clear()
        return
    
    if member_id == message.from_user.id:
        await message.answer("❌ Ви не можете видалити себе (капітана)")
        return
    
    team_id = str(team['_id'])
    success, msg = await remove_member_from_team(team_id, member_id)
    
    if success:
        user = await get_user_by_telegram_id(member_id)
        user_name = user['full_name'] if user else f"ID: {member_id}"
        await message.answer(
            f"✅ Учасника {user_name} видалено з команди",
            reply_markup=remove_keyboard()
        )
    else:
        await message.answer(f"❌ {msg}")
    
    await state.clear()


def register_handlers(dp):
    dp.include_router(router)
