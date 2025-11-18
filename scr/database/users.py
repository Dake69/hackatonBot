from scr.database.db import get_users_collection


async def create_user(telegram_id: int, username: str, full_name: str, phone: str, is_captain: bool = False):
    users = get_users_collection()
    
    user = {
        'telegram_id': telegram_id,
        'username': username,
        'full_name': full_name,
        'phone': phone,
        'is_captain': is_captain,
        'team_id': None
    }
    
    result = await users.insert_one(user)
    return str(result.inserted_id)


async def get_user_by_telegram_id(telegram_id: int):
    users = get_users_collection()
    user = await users.find_one({'telegram_id': telegram_id})
    return user


async def get_all_users():
    users = get_users_collection()
    cursor = users.find()
    users_list = await cursor.to_list(length=None)
    return users_list


async def update_user_team(telegram_id: int, team_id: str):
    users = get_users_collection()
    result = await users.update_one(
        {'telegram_id': telegram_id},
        {'$set': {'team_id': team_id}}
    )
    return result.modified_count > 0


async def get_users_by_team_id(team_id: str):
    users = get_users_collection()
    cursor = users.find({'team_id': team_id})
    team_users = await cursor.to_list(length=None)
    return team_users


async def get_captains():
    users = get_users_collection()
    cursor = users.find({'is_captain': True})
    captains = await cursor.to_list(length=None)
    return captains


async def user_exists(telegram_id: int):
    users = get_users_collection()
    user = await users.find_one({'telegram_id': telegram_id})
    return user is not None


async def delete_user(telegram_id: int):
    users = get_users_collection()
    result = await users.delete_one({'telegram_id': telegram_id})
    return result.deleted_count > 0


async def update_user_info(telegram_id: int, update_data: dict):
    users = get_users_collection()
    result = await users.update_one(
        {'telegram_id': telegram_id},
        {'$set': update_data}
    )
    return result.modified_count > 0
