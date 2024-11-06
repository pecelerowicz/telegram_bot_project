import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from config import BOT_TOKEN  # Import BOT_TOKEN from config.py

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Function to send a periodic message
async def periodic_message(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message to the chat at regular intervals."""
    chat_id = context.job.chat_id
    await context.bot.send_message(chat_id=chat_id, text="This is your regular update!")

# Function to start the periodic messages
async def start_sending(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start sending messages every second."""
    chat_id = update.effective_chat.id
    job_name = f"send_updates_{chat_id}"

    # Check if a job already exists to prevent duplicate jobs
    if context.job_queue.get_jobs_by_name(job_name):
        await update.message.reply_text("I'm already sending you updates every second!")
        return

    # Start a job that sends a message every second
    context.job_queue.run_repeating(periodic_message, interval=0.1, chat_id=chat_id, name=job_name)
    await update.message.reply_text("Started sending you updates every second.")

# Function to stop the periodic messages
async def stop_sending(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stop sending messages."""
    chat_id = update.effective_chat.id
    job_name = f"send_updates_{chat_id}"
    
    # Retrieve and cancel the job if it exists
    current_jobs = context.job_queue.get_jobs_by_name(job_name)
    if not current_jobs:
        await update.message.reply_text("There are no active updates to stop.")
        return

    for job in current_jobs:
        job.schedule_removal()

    await update.message.reply_text("Stopped sending you updates.")

# Main function to run the bot
def main():
    # Initialize the bot application with the token
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add handlers for "start" and "stop" commands
    application.add_handler(MessageHandler(filters.Regex("^(start)$"), start_sending))
    application.add_handler(MessageHandler(filters.Regex("^(stop)$"), stop_sending))

    # Run the bot with polling
    application.run_polling()

if __name__ == '__main__':
    main()
