from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from scr.FSM.states import RegistrationStates
from scr.keyboards.keyboards import get_phone_keyboard, get_role_keyboard, get_cancel_keyboard, remove_keyboard
from scr.database.models import create_user, create_team, join_team, get_user

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    
    if user:
        await message.answer(
            f"👋 Привіт, {user['full_name']}!\n\n"
            "Ви вже зареєстровані в системі."
        )
        return
    
    await message.answer(
        "👋 Вітаю на хакатоні!\n\n"
        "Давайте почнемо реєстрацію.\n"
        "Введіть ваше ПІБ:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_fullname)


@router.message(RegistrationStates.waiting_for_fullname, F.text == "❌ Скасувати")
async def cancel_registration(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Реєстрацію скасовано.",
        reply_markup=remove_keyboard()
    )


@router.message(RegistrationStates.waiting_for_fullname)
async def process_fullname(message: Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 3:
        await message.answer("❗️ Будь ласка, введіть коректне ПІБ (мінімум 3 символи):")
        return
    
    await state.update_data(fullname=message.text.strip())
    await message.answer(
        "📱 Тепер надішліть ваш номер телефону:\n"
        "Натисніть кнопку нижче 👇",
        reply_markup=get_phone_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_phone)


@router.message(RegistrationStates.waiting_for_phone, F.contact)
async def process_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    
    await message.answer(
        "👥 Оберіть вашу роль:\n\n"
        "👑 Капітан команди - якщо ви створюєте команду\n"
        "👤 Учасник команди - якщо ви приєднуєтесь до існуючої команди",
        reply_markup=get_role_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_role)


@router.message(RegistrationStates.waiting_for_phone)
async def process_phone_invalid(message: Message):
    await message.answer(
        "❗️ Будь ласка, використайте кнопку для надсилання номера телефону 👇",
        reply_markup=get_phone_keyboard()
    )


@router.callback_query(RegistrationStates.waiting_for_role, F.data == "role_captain")
async def process_captain_role(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    await state.update_data(is_captain=True)
    
    await callback.message.edit_text(
        "👑 Ви обрали роль капітана!\n\n"
        "Введіть назву вашої команди:"
    )
    await callback.message.answer(
        "💡 Введіть назву команди:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_team_name)


@router.callback_query(RegistrationStates.waiting_for_role, F.data == "role_member")
async def process_member_role(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    await state.update_data(is_captain=False)
    
    await callback.message.edit_text(
        "👤 Ви обрали роль учасника!\n\n"
        "Попросіть код команди у вашого капітана та введіть його нижче:"
    )
    await callback.message.answer(
        "🔑 Введіть код команди:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_team_code)


@router.message(RegistrationStates.waiting_for_team_name, F.text == "❌ Скасувати")
async def cancel_team_creation(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Реєстрацію скасовано.",
        reply_markup=remove_keyboard()
    )


@router.message(RegistrationStates.waiting_for_team_name)
async def process_team_name(message: Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 3:
        await message.answer("❗️ Будь ласка, введіть коректну назву команди (мінімум 3 символи):")
        return
    
    team_name = message.text.strip()
    await state.update_data(team_name=team_name)
    
    await message.answer(
        "👥 Вкажіть кількість учасників у вашій команді (від 1 до 6):",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_team_size)


@router.message(RegistrationStates.waiting_for_team_size, F.text == "❌ Скасувати")
async def cancel_team_size(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Реєстрацію скасовано.",
        reply_markup=remove_keyboard()
    )


@router.message(RegistrationStates.waiting_for_team_size)
async def process_team_size(message: Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer("❗️ Будь ласка, введіть число від 1 до 6:")
        return
    
    team_size = int(message.text)
    if team_size < 1 or team_size > 6:
        await message.answer("❗️ Кількість учасників має бути від 1 до 6:")
        return
    
    data = await state.get_data()
    
    await create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username or "",
        full_name=data['fullname'],
        phone=data['phone'],
        is_captain=True
    )
    
    team_id, team_code, unique_number = await create_team(data['team_name'], message.from_user.id, team_size)
    
    await message.answer(
        f"✅ Реєстрація успішна!\n\n"
        f"👤 ПІБ: {data['fullname']}\n"
        f"📱 Телефон: {data['phone']}\n"
        f"👑 Роль: Капітан команди\n\n"
        f"🎯 Команда '{data['team_name']}' створена!\n"
        f"🔢 Унікальний номер: <code>{unique_number}</code>\n"
        f"👥 Кількість учасників: {team_size}\n"
        f"🔑 Код команди: <code>{team_code}</code>\n\n"
        f"Надішліть цей код учасникам вашої команди для приєднання.",
        parse_mode="HTML",
        reply_markup=remove_keyboard()
    )
    await state.clear()


@router.message(RegistrationStates.waiting_for_team_code, F.text == "❌ Скасувати")
async def cancel_team_joining(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Реєстрацію скасовано.",
        reply_markup=remove_keyboard()
    )


@router.message(RegistrationStates.waiting_for_team_code)
async def process_team_code(message: Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 6:
        await message.answer("❗️ Будь ласка, введіть коректний код команди (6 символів):")
        return
    
    team_code = message.text.strip().upper()
    data = await state.get_data()
    
    await create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username or "",
        full_name=data['fullname'],
        phone=data['phone'],
        is_captain=False
    )
    
    success, msg = await join_team(message.from_user.id, team_code)
    
    if success:
        await message.answer(
            f"✅ Реєстрація успішна!\n\n"
            f"👤 ПІБ: {data['fullname']}\n"
            f"📱 Телефон: {data['phone']}\n"
            f"👤 Роль: Учасник команди\n\n"
            f"✅ {msg}",
            reply_markup=remove_keyboard()
        )
    else:
        await message.answer(
            f"❌ Помилка: {msg}\n\n"
            "Будь ласка, перевірте код та спробуйте ще раз:",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    await state.clear()


def register_handlers(dp):
    dp.include_router(router)
