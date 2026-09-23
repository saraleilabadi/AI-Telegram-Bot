import asyncio
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

# Use a currently supported model. Check https://ai.google.dev/gemini-api/docs/models
# for the latest stable / preview names before deploying.
MODEL_NAME = "gemini-3.1-flash-lite"

VALID_LANGUAGES = ["english", "spanish", "french", "german", "italian"]

user_states = {}


def _generate_sync(user_message, operation, language):
    """Blocking call to the Gemini API. Run this off the event loop."""
    if operation == "rewrite":
        instruction = (
            "generate an intelligent, clear, natural, and well-rewritten "
            "response while preserving the original meaning."
        )
    elif operation == "summarize":
        instruction = "generate a concise summary of the message."
    elif operation == "translate":
        instruction = f"translate the message into {language}."
    else:
        raise ValueError(f"Invalid operation: {operation}")

    result = client.models.generate_content(
        model=MODEL_NAME,
        contents=f"""For the following message:
        {instruction}
        Message: {user_message}""",
    )
    return result.text


async def ai_response(user_message, operation, language):
    # generate_content is a blocking network call; running it directly inside
    # an async handler would freeze the bot for every user until it returns.
    return await asyncio.to_thread(_generate_sync, user_message, operation, language)


async def start(update, context):
    await update.message.reply_text("Hello")


async def rewrite(update, context):
    user_id = update.effective_user.id
    user_states[user_id] = {"state": "waiting_for_text", "operation": "rewrite"}
    await update.message.reply_text("Now, send your text.")


async def summarize(update, context):
    user_id = update.effective_user.id
    user_states[user_id] = {"state": "waiting_for_text", "operation": "summarize"}
    await update.message.reply_text("Now, send your text.")


async def translate(update, context):
    user_id = update.effective_user.id
    user_states[user_id] = {"state": "waiting_for_language", "operation": "translate"}
    await update.message.reply_text("Please, enter your language: ")


async def cancel(update, context):
    user_id = update.effective_user.id
    if user_states.pop(user_id, None) is not None:
        await update.message.reply_text("Cancelled. Use /help to see what you can do.")
    else:
        await update.message.reply_text("Nothing to cancel.")


async def help_command(update, context):
    help_text = (
        "Available commands:\n"
        "/help - Show available commands\n"
        "/start - Start the bot\n"
        "/rewrite - Rewrite your text\n"
        "/summarize - Summarize your text\n"
        "/translate - Translate your text\n"
        "/cancel - Cancel the current operation\n"
    )
    await update.message.reply_text(help_text)


async def handle_message(update, context):
    user_message = update.message.text
    user_id = update.effective_user.id
    user_data = user_states.get(user_id)
    if not user_data:
        await update.message.reply_text("Please use a command first.")
        return

    operation = user_data["operation"]

    if user_data["state"] == "waiting_for_language":
        if user_message.strip().lower() in VALID_LANGUAGES:
            user_data["language"] = user_message.strip()
            user_data["state"] = "waiting_for_text"
            await update.message.reply_text("Now, send your text.")
        else:
            await update.message.reply_text(
                "Please enter a valid language like English, Spanish, French, German, or Italian."
            )
        return

    language = user_data.get("language")

    try:
        response = await ai_response(user_message, operation, language)
    except Exception as e:
        print(e)
        await update.message.reply_text(
            "Something went wrong. Please try again, or send /cancel to start over."
        )
        return

    del user_states[user_id]
    await update.message.reply_text(response)


def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("rewrite", rewrite))
    application.add_handler(CommandHandler("summarize", summarize))
    application.add_handler(CommandHandler("translate", translate))
    application.add_handler(CommandHandler("cancel", cancel))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()


if __name__ == "__main__":
    main()