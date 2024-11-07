import asyncio
from telegram import Update
from telegram.ext import ContextTypes

# Mock vocabulary list in Polish
vocabulary_list = [
    {"polish_word": "wytrwałość", "english_word": "perseverance"},
    {"polish_word": "wdzięczność", "english_word": "gratitude"},
    {"polish_word": "empatia", "english_word": "empathy"}
]

# State tracking for user interactions
user_state = {}


# Function to reset the user's state and send an error message
async def reset_and_notify(update: Update, message: str) -> None:
    """Reset the user's state and notify them with a message."""
    chat_id = update.effective_chat.id
    user_state[chat_id] = {"index": 0, "awaiting_disclose": False, "awaiting_know_check": False}
    await update.message.reply_text(message)


# Get the next vocabulary word in Polish
async def send_vocabulary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the next word in Polish when user types 's' or 'S'."""
    chat_id = update.effective_chat.id
    user_data = user_state.setdefault(chat_id, {"index": 0, "awaiting_disclose": False, "awaiting_know_check": False})

    # Check if the user is in the middle of a different flow
    if user_data["awaiting_disclose"] or user_data["awaiting_know_check"]:
        await reset_and_notify(update, "Invalid input. Please start over by typing 's' to get a new word.")
        return

    # Get the next vocabulary word
    if user_data["index"] < len(vocabulary_list):
        word = vocabulary_list[user_data["index"]]["polish_word"]
        user_data["awaiting_disclose"] = True  # Set state to wait for disclose
        await update.message.reply_text(f"{word}")
    else:
        await update.message.reply_text("You've gone through all the vocabulary words!")


# Disclose the English translation
async def disclose_definition(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the English translation when user types 'd' or 'D'."""
    chat_id = update.effective_chat.id
    user_data = user_state.get(chat_id)

    # Check if the user is in the correct state
    if not (user_data and user_data.get("awaiting_disclose")):
        await reset_and_notify(update, "Invalid input. Please start over by typing 's' to get a new word.")
        return

    # Provide the English translation
    word_pair = vocabulary_list[user_data["index"]]
    await update.message.reply_text(f"{word_pair['english_word']}")
    user_data["awaiting_disclose"] = False
    user_data["awaiting_know_check"] = True  # Set state to wait for know check

    # Wait for 2 seconds before asking "Did you know this word?"
    await asyncio.sleep(2)
    await update.message.reply_text("Did you know this word? (y/n)")


# Handle response to "Did you know?" question
async def process_know_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process user response 'y' or 'n' for knowing the word."""
    chat_id = update.effective_chat.id
    user_data = user_state.get(chat_id)

    # Check if the user is in the correct state
    if not (user_data and user_data.get("awaiting_know_check")):
        await reset_and_notify(update, "Invalid input. Please start over by typing 's' to get a new word.")
        return

    # Process the response
    response = update.message.text.lower()

    if response == "y":
        await update.message.reply_text("ok")
    elif response == "n":
        await update.message.reply_text("ok")
    else:
        await reset_and_notify(update, "Invalid input. Please start over by typing 's' to get a new word.")
        return

    # Move to the next word in the list and reset the state
    user_data["index"] += 1
    user_data["awaiting_know_check"] = False


# Catch-all handler for invalid input
async def handle_unexpected_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle any unexpected input by resetting the flow."""
    await reset_and_notify(update, "Invalid input. Please start over by typing 's' to get a new word.")
