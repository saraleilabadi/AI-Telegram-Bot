import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from google import genai


load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_KEY = os.getenv("GEMINI_API_KEY")


if not API_KEY:
    print("GEMINI_API_KEY not found in environment variables. Please set it in the .env file.")
    exit()

if not TOKEN:
    print("TELEGRAM_BOT_TOKEN not found in environment variables.")
    exit()

client = genai.Client(api_key=API_KEY)

user_states = {}


def ai_response(user_message, user_state, language):   
    if user_state == "rewrite":
        prompt = """generate an intelligent, clear,
        natural, and well-rewritten response while preserving the original meaning."""
    elif user_state == "summarize":
        prompt = "generate a concise summary of the message."
    elif user_state == "translate":
        prompt = f"translate the message into the {language}."
    else:
         raise ValueError("Invalid user state")

    result = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=f"""For the following message:
        {prompt}
        Message: {user_message}"""
    )
    return result.text


async def start(update, context):
    await update.message.reply_text("Hello")

async def rewrite(update, context):
    user_id = update.effective_user.id
    user_states[user_id] = {
                            "state": "waiting_for_text",
                            "operation": "rewrite"
                            }
    print(user_states)
    await update.message.reply_text("Now, send your text.")

async def summarize(update, context):
    user_id = update.effective_user.id
    user_states[user_id] = {
                            "state": "waiting_for_text",
                            "operation": "summarize"
                            }
    print(user_states)
    await update.message.reply_text("Now, send your text.")

async def translate(update, context):
    user_id = update.effective_user.id
    user_states[user_id] = {
                            "state": "waiting_for_language",
                            "operation": "translate"
                            }
    await update.message.reply_text("Please, enter your language: ")


async def handle_message(update, context):
    user_message = update.message.text
    user_id = update.effective_user.id
    user_data = user_states.get(user_id)
    if not user_data:
        await update.message.reply_text("Please use a command first.")
        return
    
    user_state = user_data["operation"]
    if user_data["state"] == "waiting_for_language":
        if user_message.strip().lower() in ["english", "spanish", "french", "german", "italian"]:
            user_data["language"] = user_message.strip()
            user_data["state"] = "waiting_for_text"
            await update.message.reply_text("Now, send your text.")
        else:
            await update.message.reply_text("Please enter a valid language like English, Spanish, French, German, or Italian.")
        return
    
    language = user_data.get("language")

    print(user_state)

    try:
        response = ai_response(user_message, user_state, language)
    
    except Exception as e:
        print(e)
        await update.message.reply_text("Something went wrong. Please try again.")
        return
    del user_states[user_id]
    await update.message.reply_text(response)


    async def help(update, context):
        help_text = (
            "Available commands:\n"
            "/help - Show available commands\n"
            "/start - Start the bot\n"
            "/rewrite - Rewrite your text\n"
            "/summarize - Summarize your text\n"
            "/translate - Translate your text\n"
        )
        await update.message.reply_text(help_text)


def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(CommandHandler("help", help))

    application.add_handler(CommandHandler("rewrite", rewrite))

    application.add_handler(CommandHandler("summarize", summarize))

    application.add_handler(CommandHandler("translate", translate))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()