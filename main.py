from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config import TOKEN
from handlers import start, rewrite, summarize, translate, cancel, help_command, handle_message


def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("rewrite", rewrite))
    application.add_handler(CommandHandler("summarize", summarize))
    application.add_handler(CommandHandler("translate", translate))
    application.add_handler(CommandHandler("cancel", cancel))

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    application.run_polling()


if __name__ == "__main__":
    main()