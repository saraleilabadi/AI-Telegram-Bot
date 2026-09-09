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

client = genai.Client(api_key=API_KEY)

user_states = {}


def ai_response(user_message, user_state):
        
    
    if user_state == "rewrite":
            prompt = """generate an intelligent, clear,
        natural, and well-rewritten response while preserving the original meaning."""
    elif user_state == "summarize":
            prompt = "generate a concise summary of the message."
    elif user_state == "translate":
            prompt = "translate the message into the specified language."
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
    user_states[user_id] = "rewrite"
    print(user_states)
    await update.message.reply_text("Now, send your text.")


async def handle_message(update, context):
    user_message = update.message.text
    user_id = update.effective_user.id
    user_state = user_states.get(user_id)
    if user_state == "rewrite":
        print(user_state)

        try:
            response = ai_response(user_message, user_state)
        except ValueError as e:
            await update.message.reply_text("Invalid user state. Please use /rewrite commands first.")
            return
        except Exception as e:
            print(e)
            await update.message.reply_text("Something went wrong. Please try again.")
            return
        del user_states[user_id]
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("Please use the /rewrite command first to rewrite your text.")

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(CommandHandler("rewrite", rewrite))  

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()