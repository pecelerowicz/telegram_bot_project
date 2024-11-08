import logging

from telegram.ext import ApplicationBuilder, MessageHandler, filters

import service  # Import the services module
from config import BOT_TOKEN

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Initialize the bot application with the token from config.py
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers for each command and interaction
    app.add_handler(MessageHandler(filters.Regex(r'^[sS]$'), service.send_vocabulary))
    app.add_handler(MessageHandler(filters.Regex(r'^[dD]$'), service.disclose_definition))
    app.add_handler(MessageHandler(filters.Regex(r'^[yYnN]$'), service.process_know_response))
    app.add_handler(MessageHandler(filters.ALL, service.handle_unexpected_input))  # Catch-all for invalid input

    # Run the bot
    app.run_polling()

if __name__ == '__main__':
    main()
