import os

# Load environment variables from .env file if using it
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")  # Bot Token from @BotFather
ADMIN_ID = os.getenv("ADMIN_ID")     # Your Telegram user ID for restricting access
