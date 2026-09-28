from telegram import Update
from telegram.ext import ContextTypes

from ai_service import ai_response
from config import VALID_LANGUAGES
from state import user_states


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello")


async def rewrite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    user_states[user_id] = {
        "state": "waiting_for_text",
        "operation": "rewrite"
    }

    await update.message.reply_text("Now, send your text.")


async def summarize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    user_states[user_id] = {
        "state": "waiting_for_text",
        "operation": "summarize"
    }

    await update.message.reply_text("Now, send your text.")


async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    user_states[user_id] = {
        "state": "waiting_for_language",
        "operation": "translate"
    }

    await update.message.reply_text("Please, enter your language:")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_states.pop(user_id, None) is not None:
        await update.message.reply_text(
            "Cancelled. Use /help to see what you can do."
        )
    else:
        await update.message.reply_text("Nothing to cancel.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = update.effective_user.id

    state_data = user_states.get(user_id)

    if not state_data:
        await update.message.reply_text("Please use a command first.")
        return

    if state_data["state"] == "waiting_for_language":

        if user_message.strip().lower() in VALID_LANGUAGES:
            state_data["language"] = user_message.strip().lower()
            state_data["state"] = "waiting_for_text"

            await update.message.reply_text("Now, send your text.")

        else:
            await update.message.reply_text(
                "Please enter a valid language like English, "
                "Spanish, French, German, or Italian."
            )

        return

    operation = state_data["operation"]
    language = state_data.get("language")

    try:
        response = await ai_response(
            user_message,
            operation,
            language
        )

    except Exception as e:
        print(e)

        await update.message.reply_text(
            "Something went wrong. Please try again, "
            "or send /cancel to start over."
        )

        return

    del user_states[user_id]

    await update.message.reply_text(response)