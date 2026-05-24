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

from intent_engine import detect_intent

from memory_manager import (
    load_contacts,
    extract_task,
    complete_task
)

from semantic_task_engine import (
    create_semantic_task,
    load_tasks,
    save_tasks
)

from reminder_scheduler import (
    calculate_next_reminder
)

from daily_summary import (
    generate_daily_summary
)

from conversation_memory import (
    get_chat_state,
    update_chat_state,
    clear_chat_state,
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

from task_merge_engine import (
    merge_items
)

from relationship_memory import (
    update_relationship_memory
)

from daily_brain import (
    generate_brain_summary
)

from entity_memory_engine import (

    update_entity,

    get_pending_entities,

    complete_entity

)

from entity_extractor import (
    extract_entities
)

from context_builder import (
    build_conversation_context
)

from conversation_window_engine import (
    build_conversation_windows
)

from item_extractor import (
    extract_items_semantically
)

from entity_resolution_engine import (
    resolve_entities
)
# =====================================
# ENV
# =====================================

load_dotenv()


# =====================================
# ENV VALIDATION — fail fast with
# a clear message if any var is missing
# =====================================

_REQUIRED_ENV = [
    "API_ID",
    "API_HASH",
    "BOT_TOKEN",
    "ADMIN_USER_ID",
    "SESSION_STRING",
    "GROQ_API_KEY",
    "GEMINI_API_KEY",
]

_missing = [k for k in _REQUIRED_ENV if not os.getenv(k)]

if _missing:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.critical(
        "Missing required environment variables: %s — "
        "add them to your .env file and restart.",
        ", ".join(_missing)
    )
    raise SystemExit(1)

API_ID = int(os.getenv("API_ID", "0"))

API_HASH = os.getenv("API_HASH")

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))

SESSION_STRING = os.getenv("SESSION_STRING")


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

from config import PROCESSED_MESSAGES_FILE as PROCESSED_FILE


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

        logging.exception("load_processed_messages failed")

        return {}


def save_processed_messages(data):

    try:

        with open(
            PROCESSED_FILE,
            "w"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )

    except Exception:

        logging.exception(
            "save_processed_messages failed — "
            "messages may be reprocessed on next run "
            "[file=%s]",
            PROCESSED_FILE
        )


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
    # Daily Summary Engine
    # =================================

    current_hour = datetime.now().hour
    
    if current_hour == 21:
    
        summary = (
            generate_daily_summary()
        )
    
        brain_summary = (
            generate_brain_summary()
        )
    
        await bot.send_message(
            chat_id=ADMIN_USER_ID,
            text=brain_summary
        )
    
        await bot.send_message(
            chat_id=ADMIN_USER_ID,
            text=summary
        )
    
        logging.info(
            "Daily summary sent"
        )
    # =================================
    # Scheduled Reminder Engine
    # =================================

    tasks = load_tasks()

    pending_tasks = []

    for task in tasks:

        if task.get("status") != "PENDING":

            continue

        next_reminder = (
            calculate_next_reminder(
                task
            )
        )

        if datetime.now() >= next_reminder:

            pending_tasks.append(task)

    if pending_tasks:

        reminder_text = (
            "📌 Pending Reminders\n\n"
        )

        for task in pending_tasks:

            priority = task.get(
                "priority",
                "NORMAL"
            )

            if priority == "CRITICAL":

                reminder_prefix = "🚨"

            elif priority == "URGENT":

                reminder_prefix = "⚠️"

            else:

                reminder_prefix = "📌"

            items_text = ""

            if task.get("items"):

                for item in task.get("items", []):

                    items_text += (
                        f"- {item}\n"
                    )

            reminder_text += (

                f"{reminder_prefix} "
                f"[{priority}] "
                f"{task.get('type', 'GENERAL')}\n\n"

                f"{items_text}\n"

                f"From: "
                f"{task.get('from', 'Unknown')}\n\n"

            )

        reminder_text += (
            "\n✅ Completion Examples:\n"
            "done groceries\n"
            "completed medicines"
        )

        await bot.send_message(
            chat_id=ADMIN_USER_ID,
            text=reminder_text
        )

        logging.info(
            "Scheduled reminders sent"
        )

    dialogs = await client.get_dialogs()

    for dialog in dialogs:

        # =============================
        # Skip unwanted chats
        # =============================

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

            elif msg.gif:

                incoming_messages.append(
                    "[GIF]"
                )

            elif msg.sticker:

                incoming_messages.append(
                    "[STICKER]"
                )

            elif msg.photo:

                incoming_messages.append(
                    "[PHOTO]"
                )

        if not incoming_messages:
            continue

        conversation_windows = (
            build_conversation_windows(
                incoming_messages
            )
        )
                
        for window in conversation_windows:
        
            message_text = " ".join(
                window.get("messages", [])
            ).strip()
        
            if not message_text:
        
                continue
        
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
            
                entities = extract_entities(
                    message_text
                )
            
                for entity in entities:
            
                    entity_name = entity.get("name", "").strip()

                    if not entity_name:

                        logging.warning(
                            "Skipping entity with empty name "
                            "[dialog=%s] — likely malformed LLM output",
                            dialog.name
                        )

                    else:

                        update_entity(

                            dialog.id,

                            entity_name,

                            entity.get("status", "MISSING_DETAILS")

                        )
                    
                pending_entities = (
                    get_pending_entities(
                        dialog.id
                    )
                )
                
                resolved_entities = (
                    resolve_entities(
                
                        message_text,
                
                        pending_entities
                
                    )
                )
                
                for resolved in resolved_entities:
                
                    complete_entity(
                
                        dialog.id,
                
                        resolved
                
                    )
                
                
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
                # Follow-up Semantic Merge
                # =============================
                if is_followup:
            
                    tasks = load_tasks()
            
                    latest_task = None
            
                    for task in reversed(tasks):
            
                        if (
                            task.get("from") == dialog.name
                            and
                            task.get("status") == "PENDING"
                        ):
            
                            latest_task = task
            
                            break
            
                    if latest_task:
            
                        new_items = (
                            extract_items_semantically(
                                clean_task
                            )
                        )
                                
                        latest_task.setdefault("items", [])
                        latest_task["items"] = (
                            merge_items(
                                latest_task.get("items", []),
                                new_items
                            )
                        )
            
                        save_tasks(tasks)
            
                    else:
            
                        create_semantic_task(
            
                            message=clean_task,
            
                            sender=dialog.name,
            
                            priority=priority
            
                        )
            
                        update_relationship_memory(
            
                            dialog.name,
            
                            clean_task
            
                        )
            
                else:
            
                    create_semantic_task(
            
                        message=clean_task,
            
                        sender=dialog.name,
            
                        priority=priority
            
                    )
            
                    update_relationship_memory(
            
                        dialog.name,
            
                        clean_task
            
                    )
            
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

                    conversation_context = (
                        build_conversation_context(
                            dialog.id,
                            dialog.name
                        )
                    )
                
                    assistant_reply = (
                        generate_clarification_reply(
                            relationship,
                            clean_task,
                            conversation_context
                        )
                    )

                else:

                    conversation_context = (
                        build_conversation_context(
                            dialog.id,
                            dialog.name
                        )
                    )
                
                    assistant_reply = (
                        generate_assistant_reply(
                            relationship,
                            intent,
                            message_text,
                            phase,
                            conversation_context
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
            # CORRECTION CHECK
            # =================================
            
            elif intent == "CORRECTION":

                conversation_context = (
                        build_conversation_context(
                            dialog.id,
                            dialog.name
                        )
                    )
                
                assistant_reply = (
                    generate_assistant_reply(
                        relationship,
                        intent,
                        message_text,
                        phase,
                        conversation_context
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
            # STATUS CHECK
            # =================================

            elif intent == "STATUS_CHECK":

                conversation_context = (
                        build_conversation_context(
                            dialog.id,
                            dialog.name
                        )
                    )
            
                assistant_reply = (
                    generate_assistant_reply(
                        relationship,
                        intent,
                        message_text,
                        phase,
                        conversation_context
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

                conversation_context = (
                        build_conversation_context(
                            dialog.id,
                            dialog.name
                        )
                    )
            
                assistant_reply = (
                    generate_assistant_reply(
                        relationship,
                        intent,
                        message_text,
                        phase,
                        conversation_context
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

                conversation_context = (
                        build_conversation_context(
                            dialog.id,
                            dialog.name
                        )
                    )

                assistant_reply = (
                    generate_assistant_reply(
                        relationship,
                        intent,
                        message_text,
                        phase,
                        conversation_context
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
        
                conversation_context = (
                    build_conversation_context(
                        dialog.id,
                        dialog.name
                    )
                )
        
                try:
        
                    ai_reply = (
                        generate_assistant_reply(
        
                            relationship,
        
                            "GENERAL",
        
                            message_text,
        
                            phase,
        
                            conversation_context
        
                        )
                    )
        
                except Exception:
        
                    logging.exception(
                        "generate_assistant_reply failed in GENERAL block "
                        "[dialog=%s message=%s]",
                        dialog.name, message_text
                    )
        
                    ai_reply = (
                        "Unable to generate reply."
                    )
        
                notification_text = f"""
            ⚠️ Manual Attention Required
        
            👤 Chat:
            {dialog.name}
        
            💬 Message:
            {message_text}
        
            🧠 Context:
            {json.dumps(conversation_context, indent=2)}
        
            🤖 Suggested Draft:
            {ai_reply}
            """
        
                await bot.send_message(
                    chat_id=ADMIN_USER_ID,
                    text=notification_text
                )

        processed[chat_id] = (message_id)

        save_processed_messages(processed)


# =====================================
# Run
# =====================================

with client:

    client.loop.run_until_complete(
        process_messages()
    )

logging.info("Script completed")