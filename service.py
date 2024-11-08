import asyncio
from telegram import Update
from telegram.ext import ContextTypes
import csv
import random

# State tracking for user interactions
user_state = {}

# Variable to store the current word pair for the cycle
current_word_pair = None

# Function to retrieve the next vocabulary word pair and manage index progression
def get_next_word_pair(filename="vocabulary.txt"):
    """Retrieve a random word pair from the vocabulary file."""
    vocabulary_list = []

    # Open the .txt file and read the vocabulary data
    with open(filename, mode="r", encoding="utf-8") as file:
        # Skip the header line
        next(file)

        # Process each line
        for line in file:
            # Split by semicolon and strip any surrounding whitespace
            parts = line.strip().split(';')
            if len(parts) >= 6:  # Ensure there are enough parts
                vocabulary_list.append({
                    "index": int(parts[0].strip()),
                    "english_word": parts[1].strip(),
                    "polish_word": parts[2].strip(),
                    "known_count": int(parts[3].strip()),
                    "unknown_count": int(parts[4].strip()),
                    "mode": int(parts[5].strip())
                })

    # Return a random word pair from the list
    return random.choice(vocabulary_list) if vocabulary_list else None

# Function to reset the user's state and send an error message
async def reset_and_notify(update: Update, message: str) -> None:
    """Reset the user's state and notify them with a message."""
    chat_id = update.effective_chat.id
    user_state[chat_id] = {"awaiting_disclose": False, "awaiting_know_check": False}
    await update.message.reply_text(message)

# Send the next Polish vocabulary word
async def send_vocabulary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the next word in Polish when user types 's' or 'S'."""
    global current_word_pair
    chat_id = update.effective_chat.id
    user_data = user_state.setdefault(chat_id, {"awaiting_disclose": False, "awaiting_know_check": False})

    # Check if the user is in the middle of a different flow
    if user_data["awaiting_disclose"] or user_data["awaiting_know_check"]:
        await reset_and_notify(update, "Invalid input. Please start over by typing 's' to get a new word.")
        return

    # Get the next vocabulary word pair and store it globally for this cycle
    current_word_pair = get_next_word_pair()
    if current_word_pair:
        polish_word = current_word_pair["polish_word"]
        user_data["awaiting_disclose"] = True  # Set state to wait for disclose
        await update.message.reply_text(f"{polish_word}")
    else:
        await update.message.reply_text("You've gone through all the vocabulary words!")

# Disclose the English translation
async def disclose_definition(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the English translation when user types 'd' or 'D'."""
    global current_word_pair
    chat_id = update.effective_chat.id
    user_data = user_state.get(chat_id)

    # Check if the user is in the correct state
    if not (user_data and user_data.get("awaiting_disclose")):
        await reset_and_notify(update, "Invalid input. Please start over by typing 's' to get a new word.")
        return

    # Reveal the English translation for the current Polish word pair
    if current_word_pair:
        await update.message.reply_text(f"{current_word_pair['english_word']}")
        user_data["awaiting_disclose"] = False
        user_data["awaiting_know_check"] = True  # Set state to wait for know check

        # Wait for 2 seconds before asking "Did you know this word? (y/n)")
        await asyncio.sleep(2)
        await update.message.reply_text("Did you know this word? (y/n)")
    else:
        await update.message.reply_text("No words to disclose.")

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

    if response in ["y", "n"]:
        await update.message.reply_text("ok")
        user_data["awaiting_know_check"] = False
    else:
        await reset_and_notify(update, "Invalid input. Please start over by typing 's' to get a new word.")

# Catch-all handler for invalid input
async def handle_unexpected_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle any unexpected input by resetting the flow."""
    await reset_and_notify(update, "Invalid input. Please start over by typing 's' to get a new word.")
