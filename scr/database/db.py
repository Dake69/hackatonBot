from motor.motor_asyncio import AsyncIOMotorClient
from config import CONN_LINK

client = None
db = None

users_collection = None
teams_collection = None


async def init_db():
    global client, db, users_collection, teams_collection
    
    client = AsyncIOMotorClient(CONN_LINK)
    db = client['hackathon_bot']
    
    users_collection = db['users']
    teams_collection = db['teams']
    
    await users_collection.create_index('telegram_id', unique=True)
    await teams_collection.create_index('code', unique=True)
    await teams_collection.create_index('unique_number', unique=True)
    
    print("✅ База даних підключена успішно!")


async def close_db():
    global client
    if client:
        client.close()
        print("❌ З'єднання з базою даних закрито")


def get_users_collection():
    return users_collection


def get_teams_collection():
    return teams_collection
