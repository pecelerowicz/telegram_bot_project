import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from config import BOT_TOKEN
import services  # Import the services module

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Initialize the bot application with the token from config.py
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers for each command and interaction
    app.add_handler(MessageHandler(filters.Regex(r'^[sS]$'), services.send_vocabulary))
    app.add_handler(MessageHandler(filters.Regex(r'^[dD]$'), services.disclose_definition))
    app.add_handler(MessageHandler(filters.Regex(r'^[yYnN]$'), services.process_know_response))
    app.add_handler(MessageHandler(filters.ALL, services.handle_unexpected_input))  # Catch-all for invalid input

    # Run the bot
    app.run_polling()

if __name__ == '__main__':
    main()
