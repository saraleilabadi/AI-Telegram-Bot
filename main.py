import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update, context):
    await update.message.reply_text("Hello")

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.run_polling()

if __name__ == "__main__":
    main()