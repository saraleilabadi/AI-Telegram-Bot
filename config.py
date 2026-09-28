import os

from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_KEY = os.getenv("GEMINI_API_KEY")

MODEL_NAME = "gemini-3.6-flash"

VALID_LANGUAGES = [
    "english",
    "spanish",
    "french",
    "german",
    "italian",
]


if not API_KEY:
    print("GEMINI_API_KEY not found in environment variables. Please set it in the .env file.")
    exit()

if not TOKEN:
    print("TELEGRAM_BOT_TOKEN not found in environment variables.")
    exit()