import os
import json
import logging
import asyncio

from datetime import datetime

from dotenv import load_dotenv

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon import Button

from telegram import Bot

from ai_router import generate_reply

from intent_engine import detect_intent

from memory_manager import (
    add_task,
    get_pending_tasks,
    load_contacts,
    extract_task,
    update_last_reminded,
    task_exists,
    load_tasks,
    save_tasks,
    complete_task
)

from conversation_memory import (
    get_chat_state,
    update_chat_state,
    clear_chat_state,
    set_conversation_state,
    is_conversation_active
)

from assistant_reply_generator import (
    generate_assistant_reply
)

from clarification_engine import (
    needs_clarification,
    generate_clarification_reply
)

from conversation_phase import (
    determine_phase
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
# Logging
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
# Silent Hours
# =====================================

def is_silent_hours():

    current_hour = (
        datetime.now().hour
    )

    return (
        current_hour >= 1
        and current_hour <= 7
    )


async def human_delay():

    await asyncio.sleep(2)


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
# Processed Message Helpers
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
# Update Existing Task
# =====================================

def update_existing_task(
    existing_task,
    new_items
):

    tasks = load_tasks()

    for task in tasks:

        if task["message"] == existing_task:

            # Avoid duplicate appends

            if (
                new_items.lower()
                not in
                task["message"].lower()
            ):

                task["message"] += (
                    ", "
                    + new_items
                )

            break

    save_tasks(tasks)


# =====================================
# Telegram Client
# =====================================

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)


# =====================================
# Main Logic
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

            created_at = datetime.fromisoformat(
                task["created_at"]
            )

            hours_old = (
                datetime.now() - created_at
            ).total_seconds() / 3600

            if hours_old > 72:

                task["priority"] = (
                    "CRITICAL"
                )

            elif hours_old > 48:

                task["priority"] = (
                    "URGENT"
                )

            elif hours_old > 24:

                task["priority"] = (
                    "HIGH"
                )

            if task["priority"] == (
                "CRITICAL"
            ):

                reminder_prefix = "🚨"

            elif task["priority"] == (
                "URGENT"
            ):

                reminder_prefix = "⚠️"

            else:

                reminder_prefix = "📌"

            reminder_text += (
                f"#{index} • "
                f"{reminder_prefix} "
                f"[{task['priority']}]\n"
                f"{task['message']}\n"
                f"From: {task['from']}\n\n"
            )

            update_last_reminded(
                index - 1
            )

        reminder_text += (
            "\n✅ To complete:\n"
            "done 1\n"
            "completed 2\n"
            "finished 3"
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

        messages = await client.get_messages(
            dialog.id,
            limit=dialog.unread_count
        )

        if not messages:
            continue

        incoming_messages = []

        latest_message_id = None

        for msg in reversed(messages):

            if not msg:
                continue

            if msg.out:
                continue

            latest_message_id = msg.id

            if msg.message:

                incoming_messages.append(
                    msg.message
                )

        if not incoming_messages:
            continue

        message_text = " ".join(
            incoming_messages
        )[:2000]

        chat_id = str(dialog.id)

        message_id = latest_message_id

        last_processed = (
            processed.get(chat_id)
        )

        if last_processed == message_id:

            continue

        logging.info(
            f"Incoming unread context: "
            f"{message_text}"
        )

        relationship = contacts.get(
            dialog.name,
            "GENERAL"
        )

        chat_state = get_chat_state(
            dialog.id
        )

        intent = detect_intent(
            message_text
        )

        phase = determine_phase(
            intent,
            message_text
        )

        logging.info(
            f"Intent: {intent}"
        )

        logging.info(
            f"Phase: {phase}"
        )

        # =================================
        # Active Conversation Window
        # =================================

        conversation_active = (
            is_conversation_active(
                dialog.id
            )
        )

        is_followup = (

            conversation_active

            and

            chat_state.get(
                "active_task"
            )

        )

        # =================================
        # TASK / FOLLOWUP TASK
        # =================================

        if intent in [
            "TASK",
            "FOLLOWUP_TASK"
        ]:

            clean_task = extract_task(
                message_text
            )

            clarification_needed = (
                needs_clarification(
                    clean_task
                )
            )

            priority = "NORMAL"

            if relationship == "WIFE":

                priority = "CRITICAL"

            elif relationship == "FAMILY":

                priority = "HIGH"

            elif relationship == "BOSS":

                priority = "URGENT"

            # =============================
            # FOLLOWUP UPDATE
            # =============================

            if is_followup:

                existing_task = (
                    chat_state.get(
                        "active_task",
                        ""
                    )
                )

                update_existing_task(
                    existing_task,
                    clean_task
                )

                updated_task = (
                    existing_task
                    + ", "
                    + clean_task
                )

                update_chat_state(

                    dialog.id,

                    {

                        "awaiting_clarification":
                        clarification_needed,

                        "active_task":
                        updated_task

                    }

                )

                clean_task = updated_task

            else:

                if not task_exists(clean_task):

                    task = {

                        "from": dialog.name,

                        "chat_id": dialog.id,

                        "message": clean_task,

                        "original_message":
                        message_text,

                        "status": "PENDING",

                        "priority": priority,

                        "created_at": str(
                            datetime.now()
                        ),

                        "last_reminded":
                        None
                    }

                    add_task(task)

                update_chat_state(

                    dialog.id,

                    {

                        "awaiting_clarification":
                        clarification_needed,

                        "active_task":
                        clean_task

                    }

                )

            # =============================
            # Generate Reply
            # =============================

            if clarification_needed:

                assistant_reply = (
                    generate_clarification_reply(
                        relationship,
                        clean_task
                    )
                )

            else:

                assistant_reply = (
                    generate_assistant_reply(
                        relationship,
                        intent,
                        message_text,
                        phase
                    )
                )

            try:

                if not is_silent_hours():

                    await human_delay()

                    if clarification_needed:

                        await client.send_message(
                            entity=dialog.id,
                            message=assistant_reply,
                            reply_to=latest_message_id,
                            buttons=Button.force_reply(
                                single_use=True,
                                placeholder="Reply here..."
                            )
                        )

                    else:

                        await client.send_message(
                            entity=dialog.id,
                            message=assistant_reply,
                            reply_to=latest_message_id
                        )

            except Exception as e:

                logging.exception(e)

        # =================================
        # TASK COMPLETION
        # =================================

        elif intent == "TASK_COMPLETION":

            completed = complete_task(
                message_text
            )

            if completed:

                reply = (
                    "Perfect ❤️ "
                    "I've marked it completed."
                )

                clear_chat_state(
                    dialog.id
                )

            else:

                reply = (
                    "I couldn't find that task."
                )

            try:

                if not is_silent_hours():

                    await human_delay()

                    await client.send_message(
                        entity=dialog.id,
                        message=reply,
                        reply_to=latest_message_id
                    )

            except Exception as e:

                logging.exception(e)

        # =================================
        # STATUS CHECK
        # =================================

        elif intent == "STATUS_CHECK":

            assistant_reply = (
                generate_assistant_reply(
                    relationship,
                    intent,
                    message_text,
                    phase
                )
            )

            try:

                if not is_silent_hours():

                    await human_delay()

                    await client.send_message(
                        entity=dialog.id,
                        message=assistant_reply,
                        reply_to=latest_message_id
                    )

            except Exception as e:

                logging.exception(e)

        # =================================
        # ACKNOWLEDGEMENT
        # =================================

        elif intent == "ACKNOWLEDGEMENT":

            assistant_reply = (
                generate_assistant_reply(
                    relationship,
                    intent,
                    message_text,
                    phase
                )
            )

            try:

                if not is_silent_hours():

                    await human_delay()

                    await client.send_message(
                        entity=dialog.id,
                        message=assistant_reply,
                        reply_to=latest_message_id
                    )

            except Exception as e:

                logging.exception(e)

        # =================================
        # EMOTIONAL / CLOSURE
        # =================================

        elif intent in [
            "EMOTIONAL",
            "CLOSURE"
        ]:

            assistant_reply = (
                generate_assistant_reply(
                    relationship,
                    intent,
                    message_text,
                    phase
                )
            )

            try:

                if not is_silent_hours():

                    await human_delay()

                    await client.send_message(
                        entity=dialog.id,
                        message=assistant_reply,
                        reply_to=latest_message_id
                    )

            except Exception as e:

                logging.exception(e)

        # =================================
        # GENERAL
        # =================================

        else:

            logging.info(
                "Manual attention required"
            )

            try:

                ai_reply = generate_reply(
                    message_text
                )

            except Exception:

                ai_reply = (
                    "Unable to generate reply."
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

        processed[chat_id] = (
            message_id
        )

        save_processed_messages(
            processed
        )


# =====================================
# Run
# =====================================

with client:

    client.loop.run_until_complete(
        process_messages()
    )

logging.info("Script completed")