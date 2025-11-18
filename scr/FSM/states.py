from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    waiting_for_fullname = State()
    waiting_for_phone = State()
    waiting_for_role = State()
    waiting_for_team_name = State()
    waiting_for_team_code = State()
