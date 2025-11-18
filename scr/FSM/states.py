from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    waiting_for_fullname = State()
    waiting_for_phone = State()
    waiting_for_role = State()
    waiting_for_team_name = State()
    waiting_for_team_size = State()
    waiting_for_team_code = State()


class TeamManagementStates(StatesGroup):
    waiting_for_new_team_name = State()
    waiting_for_new_max_members = State()
    waiting_for_member_to_remove = State()
