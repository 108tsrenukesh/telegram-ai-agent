import os
import json
import logging

from dotenv import load_dotenv

from telethon import TelegramClient
from telethon.sessions import StringSession

from telegram import Bot

from ai_router import generate_reply

from intent_engine import detect_intent

from memory_manager import (
    add_task,
    get_pending_tasks,
    load_contacts
)


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

PROCESSED_FILE = (
    "processed_messages.json"
)


# =====================================
# Processed Messages Helpers
# =====================================

def load_processed_messages():

    try:

        with open(
            PROCESSED_FILE,
            "r"
        ) as file:

            return json.load(file)

    except Exception:

        return {}


def save_processed_messages(data):

    with open(
        PROCESSED_FILE,
        "w"
    ) as file:

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

    processed = (
        load_processed_messages()
    )

    contacts = load_contacts()

    logging.info(
        "Starting Telegram scan..."
    )

    await client.start()

    # =================================
    # Reminder Engine
    # =================================

    pending_tasks = (
        get_pending_tasks()
    )

    if pending_tasks:

        reminder_text = (
            "📌 Pending Reminders\n\n"
        )

        for index, task in enumerate(
            pending_tasks,
            start=1
        ):

            reminder_text += (
                f"{index}. "
                f"[TASK ID: {index - 1}] "
                f"{task['message']}\n"
                f"From: {task['from']}\n\n"
            )

        await bot.send_message(
            chat_id=ADMIN_USER_ID,
            text=reminder_text
        )

        logging.info(
            "Pending reminders sent"
        )

    dialogs = await client.get_dialogs()

    for dialog in dialogs:

        # =================================
        # Skip unwanted chats
        # =================================

        if dialog.is_channel:
            continue

        if dialog.is_group:
            continue

        if getattr(
            dialog.entity,
            "bot",
            False
        ):
            continue

        if getattr(
            dialog.entity,
            "self",
            False
        ):
            continue

        unread_count = (
            dialog.unread_count
        )

        if unread_count == 0:
            continue

        logging.info(
            f"Unread messages found in: "
            f"{dialog.name}"
        )

        # =================================
        # Fetch recent messages
        # =================================

        messages = (
            await client.get_messages(
                dialog.id,
                limit=20
            )
        )

        if not messages:
            continue

        latest_message = messages[0]

        chat_id = str(dialog.id)

        message_id = latest_message.id

        last_processed = (
            processed.get(chat_id)
        )

        if last_processed == message_id:

            logging.info(
                "Message already processed"
            )

            continue

        # =================================
        # Build combined conversation
        # =================================

        combined_messages = []

        for msg in reversed(messages):

            if not msg:
                continue

            if msg.message:

                combined_messages.append(
                    msg.message
                )

            elif msg.gif:

                combined_messages.append(
                    "[GIF]"
                )

            elif msg.sticker:

                combined_messages.append(
                    "[STICKER]"
                )

            elif msg.photo:

                combined_messages.append(
                    "[PHOTO]"
                )

        message_text = " ".join(
            combined_messages
        )[:2000]

        if not message_text:
            continue

        logging.info(
            f"Combined message: "
            f"{message_text}"
        )

        # =================================
        # Relationship Detection
        # =================================

        relationship = contacts.get(
            dialog.name,
            "GENERAL"
        )

        logging.info(
            f"Relationship: {relationship}"
        )

        # =================================
        # Intent Detection
        # =================================

        intent = detect_intent(
            message_text
        )

        logging.info(
            f"Intent detected: {intent}"
        )

        # =================================
        # TASK Intent
        # =================================

        if intent == "TASK":

            task = {

                "from": dialog.name,

                "chat_id": dialog.id,

                "message": message_text,

                "status": "PENDING"

            }

            add_task(task)

            if relationship == "FAMILY":

                assistant_reply = (
                    "Hello, this is Lucifer, "
                    "Renukesh's AI assistant. "
                    "He is currently unavailable. "
                    "I'll remind Renukesh "
                    "about this."
                )

            elif relationship == "FRIEND":

                assistant_reply = (
                    "Hey! Lucifer here, "
                    "Renukesh's AI assistant. "
                    "He is currently unavailable. "
                    "I'll remind him about this."
                )

            elif relationship == "WIFE":

                assistant_reply = (
                    "Hey Akshatha ❤️ "
                    "Lucifer here. "
                    "Got it, "
                    "I'll remind Renukesh."
                )

            else:

                assistant_reply = (
                    "Hello, this is Lucifer, "
                    "Renukesh's AI assistant. "
                    "He is currently unavailable. "
                    "I'll remind him about this."
                )

            try:

                await client.send_message(
                    entity=dialog.id,
                    message=assistant_reply
                )

                logging.info(
                    "Task acknowledgement sent"
                )

            except Exception as e:

                logging.exception(e)

            await bot.send_message(
                chat_id=ADMIN_USER_ID,
                text=(
                    f"📌 New Task Created\n\n"
                    f"From: {dialog.name}\n\n"
                    f"Message:\n"
                    f"{message_text}"
                )
            )

        # =================================
        # STATUS CHECK
        # =================================

        elif intent == "STATUS_CHECK":

            assistant_reply = (
                "Renukesh is currently "
                "unavailable. "
                "I'll check and update you."
            )

            try:

                await client.send_message(
                    entity=dialog.id,
                    message=assistant_reply
                )

                logging.info(
                    "Status acknowledgement sent"
                )

            except Exception as e:

                logging.exception(e)

            await bot.send_message(
                chat_id=ADMIN_USER_ID,
                text=(
                    f"❓ Status Check Message\n\n"
                    f"From: {dialog.name}\n\n"
                    f"Message:\n"
                    f"{message_text}"
                )
            )

        # =================================
        # GENERAL
        # =================================

        else:

            logging.info(
                "Generating AI draft..."
            )

            try:

                ai_reply = generate_reply(
                    message_text
                )

            except Exception as e:

                logging.exception(e)

                ai_reply = (
                    "Unable to generate draft"
                )

            notification_text = f"""
⚠️ Manual Attention Required

👤 Chat:
{dialog.name}

💬 Message:
{message_text}

🤖 Suggested Draft:
{ai_reply}
"""

            await bot.send_message(
                chat_id=ADMIN_USER_ID,
                text=notification_text
            )

        # =================================
        # Save Processed Message
        # =================================

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