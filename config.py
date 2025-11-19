import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CONN_LINK = os.getenv('CONN_LINK')
ADMIN_ID = os.getenv('ADMIN_ID')

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не знайдено! Додайте його у файл .env")

if not CONN_LINK:
    raise ValueError("CONN_LINK не знайдено! Додайте його у файл .env")
