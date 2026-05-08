import os
import json
import logging

from dotenv import load_dotenv

from telethon import TelegramClient
from telethon.sessions import StringSession

from telegram import (
    Bot,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from ai_router import generate_reply


# =====================================
# Load ENV variables
# =====================================

load_dotenv()

API_ID = int(os.getenv("API_ID"))

API_HASH = os.getenv("API_HASH")

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_USER_ID = int(
    os.getenv("ADMIN_USER_ID")
)

SESSION_STRING = os.getenv(
    "SESSION_STRING"
)


# =====================================
# Logging Config
# =====================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.getLogger(
    "httpx"
).setLevel(logging.WARNING)

logging.getLogger(
    "telethon"
).setLevel(logging.WARNING)


# =====================================
# Telegram Bot
# =====================================

bot = Bot(token=BOT_TOKEN)


# =====================================
# Files
# =====================================

PROCESSED_FILE = "processed_messages.json"

PENDING_FILE = "pending_replies.json"


# =====================================
# Processed Messages Helpers
# =====================================

def load_processed_messages():

    try:

        with open(PROCESSED_FILE, "r") as file:

            return json.load(file)

    except Exception as e:

        logging.exception(e)

        return {}


def save_processed_messages(data):

    with open(PROCESSED_FILE, "w") as file:

        json.dump(
            data,
            file,
            indent=4
        )


# =====================================
# Pending Replies Helpers
# =====================================

def load_pending_replies():

    try:

        with open(PENDING_FILE, "r") as file:

            return json.load(file)

    except Exception as e:

        logging.exception(e)

        return {}


def save_pending_replies(data):

    with open(PENDING_FILE, "w") as file:

        json.dump(
            data,
            file,
            indent=4
        )


# =====================================
# Telethon Client
# =====================================

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)


# =====================================
# Main Processing Logic
# =====================================

async def process_messages():

    processed = load_processed_messages()

    pending = load_pending_replies()

    logging.info("Starting Telegram scan...")

    await client.start()

    dialogs = await client.get_dialogs()

    for dialog in dialogs:

        # ==============================
        # Skip unwanted chats
        # ==============================

        if dialog.is_channel:
            continue

        if dialog.is_group:
            continue

        if getattr(dialog.entity, "bot", False):
            continue

        if getattr(dialog.entity, "self", False):
            continue

        unread_count = dialog.unread_count

        if unread_count == 0:
            continue

        logging.info(
            f"Unread messages found in: {dialog.name}"
        )

        messages = await client.get_messages(
            dialog.id,
            limit=1
        )

        if not messages:
            continue

        latest_message = messages[0]

        chat_id = str(dialog.id)

        message_id = latest_message.id

        last_processed = processed.get(chat_id)

        if last_processed == message_id:

            logging.info(
                "Message already processed"
            )

            continue

        if not latest_message.message:
            continue

        message_text = latest_message.message

        # Prevent huge prompts

        message_text = message_text[:2000]

        logging.info("Generating AI reply...")

        try:

            ai_reply = generate_reply(
                message_text
            )

        except Exception as e:

            logging.exception(e)

            ai_reply = (
                "Unable to generate reply"
            )

        if not ai_reply:
            continue

        # ==============================
        # Unique Request ID
        # ==============================

        unique_id = (
            f"{chat_id}_{message_id}"
        )

        # ==============================
        # Save Pending Reply
        # ==============================

        pending[unique_id] = {
            "chat_id": dialog.id,
            "reply_text": ai_reply
        }

        save_pending_replies(
            pending
        )

        # ==============================
        # Inline Buttons
        # ==============================

        keyboard = [
            [
                InlineKeyboardButton(
                    "Approve",
                    callback_data=(
                        f"approve:{unique_id}"
                    )
                ),

                InlineKeyboardButton(
                    "Reject",
                    callback_data=(
                        f"reject:{unique_id}"
                    )
                )
            ]
        ]

        reply_markup = (
            InlineKeyboardMarkup(
                keyboard
            )
        )

        # ==============================
        # Notification Message
        # ==============================

        notification_text = f"""
📩 New unread message

👤 Chat:
{dialog.name}

💬 Message:
{message_text}

🤖 Suggested Reply:
{ai_reply}
"""

        await bot.send_message(
            chat_id=ADMIN_USER_ID,
            text=notification_text,
            reply_markup=reply_markup
        )

        logging.info("Notification sent")

        # ==============================
        # Save Processed Message
        # ==============================

        processed[chat_id] = message_id

        save_processed_messages(
            processed
        )


# =====================================
# Run Script
# =====================================

with client:

    client.loop.run_until_complete(
        process_messages()
    )

logging.info("Script completed")