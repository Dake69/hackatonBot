import random
import string
from scr.database.db import get_teams_collection


def generate_team_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


def generate_unique_number():
    return ''.join(random.choices(string.digits, k=6))


async def create_team(name: str, captain_id: int, max_members: int = 6):
    teams = get_teams_collection()
    
    while True:
        code = generate_team_code()
        existing_team = await teams.find_one({'code': code})
        if not existing_team:
            break
    
    while True:
        unique_number = generate_unique_number()
        existing_team = await teams.find_one({'unique_number': unique_number})
        if not existing_team:
            break
    
    team = {
        'name': name,
        'code': code,
        'unique_number': unique_number,
        'captain_id': captain_id,
        'max_members': max_members,
        'members_telegram_ids': [captain_id],
        'chat_link': None
    }
    
    result = await teams.insert_one(team)
    team_id = str(result.inserted_id)
    
    return team_id, code, unique_number


async def get_team_by_code(code: str):
    teams = get_teams_collection()
    team = await teams.find_one({'code': code.upper()})
    return team


async def get_team_by_id(team_id: str):
    teams = get_teams_collection()
    from bson import ObjectId
    team = await teams.find_one({'_id': ObjectId(team_id)})
    return team


async def get_team_by_unique_number(unique_number: str):
    teams = get_teams_collection()
    team = await teams.find_one({'unique_number': unique_number})
    return team


async def get_all_teams():
    teams = get_teams_collection()
    cursor = teams.find()
    teams_list = await cursor.to_list(length=None)
    return teams_list


async def get_team_members_count(team_id: str):
    teams = get_teams_collection()
    from bson import ObjectId
    team = await teams.find_one({'_id': ObjectId(team_id)})
    if team and 'members_telegram_ids' in team:
        return len(team['members_telegram_ids'])
    return 0


async def get_team_members_ids(team_id: str):
    teams = get_teams_collection()
    from bson import ObjectId
    team = await teams.find_one({'_id': ObjectId(team_id)})
    if team and 'members_telegram_ids' in team:
        return team['members_telegram_ids']
    return []


async def add_member_to_team(team_id: str, telegram_id: int):
    teams = get_teams_collection()
    from bson import ObjectId
    
    team = await teams.find_one({'_id': ObjectId(team_id)})
    if not team:
        return False, "Команду не знайдено"
    
    if telegram_id in team.get('members_telegram_ids', []):
        return False, "Користувач вже є в команді"
    
    if len(team.get('members_telegram_ids', [])) >= team['max_members']:
        return False, f"Команда вже заповнена ({team['max_members']} учасників)"
    
    result = await teams.update_one(
        {'_id': ObjectId(team_id)},
        {'$push': {'members_telegram_ids': telegram_id}}
    )
    
    return result.modified_count > 0, "Успішно додано до команди"


async def remove_member_from_team(team_id: str, telegram_id: int):
    teams = get_teams_collection()
    from bson import ObjectId
    
    team = await teams.find_one({'_id': ObjectId(team_id)})
    if not team:
        return False, "Команду не знайдено"
    
    if team['captain_id'] == telegram_id:
        return False, "Капітан не може покинути команду"
    
    result = await teams.update_one(
        {'_id': ObjectId(team_id)},
        {'$pull': {'members_telegram_ids': telegram_id}}
    )
    
    return result.modified_count > 0, "Успішно видалено з команди"


async def join_team(telegram_id: int, team_code: str):
    teams = get_teams_collection()
    
    team = await teams.find_one({'code': team_code.upper()})
    if not team:
        return False, "Команду з таким кодом не знайдено"
    
    if telegram_id in team.get('members_telegram_ids', []):
        return False, "Ви вже є в команді"
    
    if len(team.get('members_telegram_ids', [])) >= team['max_members']:
        return False, f"Команда вже заповнена ({team['max_members']} учасників)"
    
    team_id = str(team['_id'])
    from bson import ObjectId
    
    result = await teams.update_one(
        {'_id': ObjectId(team_id)},
        {'$push': {'members_telegram_ids': telegram_id}}
    )
    
    if result.modified_count > 0:
        return True, f"Успішно приєдналися до команди {team['name']}"
    return False, "Помилка при приєднанні до команди"


async def leave_team(telegram_id: int):
    teams = get_teams_collection()
    
    team = await teams.find_one({'members_telegram_ids': telegram_id})
    if not team:
        return False, "Ви не є в жодній команді"
    
    if team['captain_id'] == telegram_id:
        return False, "Капітан не може покинути команду. Видаліть команду."
    
    from bson import ObjectId
    result = await teams.update_one(
        {'_id': team['_id']},
        {'$pull': {'members_telegram_ids': telegram_id}}
    )
    
    if result.modified_count > 0:
        return True, f"Ви покинули команду {team['name']}"
    return False, "Помилка при виході з команди"


async def delete_team(team_id: str):
    teams = get_teams_collection()
    from bson import ObjectId
    
    result = await teams.delete_one({'_id': ObjectId(team_id)})
    return result.deleted_count > 0


async def delete_team_by_captain(captain_id: int):
    teams = get_teams_collection()
    
    result = await teams.delete_one({'captain_id': captain_id})
    return result.deleted_count > 0


async def update_team_info(team_id: str, update_data: dict):
    teams = get_teams_collection()
    from bson import ObjectId
    result = await teams.update_one(
        {'_id': ObjectId(team_id)},
        {'$set': update_data}
    )
    return result.modified_count > 0


async def get_team_by_captain_id(captain_id: int):
    teams = get_teams_collection()
    team = await teams.find_one({'captain_id': captain_id})
    return team


async def is_team_full(team_id: str):
    teams = get_teams_collection()
    from bson import ObjectId
    team = await teams.find_one({'_id': ObjectId(team_id)})
    if team:
        current_count = len(team.get('members_telegram_ids', []))
        return current_count >= team['max_members']
    return False
