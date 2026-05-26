import json
import logging
import os

from datetime import datetime

from ai_router import generate_reply

from config import TASKS_FILE, CONTACTS_FILE

logger = logging.getLogger(__name__)


# =====================================
# TASK FILE HELPERS
# =====================================

def load_tasks():

    if not os.path.exists(TASKS_FILE):

        return []

    try:

        with open(TASKS_FILE, "r") as file:

            return json.load(file)

    except Exception:

        logger.exception(
            "load_tasks failed [file=%s]",
            TASKS_FILE
        )

        return []


def save_tasks(tasks):

    try:

        with open(TASKS_FILE, "w") as file:

            json.dump(tasks, file, indent=4)

    except Exception:

        logger.exception(
            "save_tasks failed [file=%s]",
            TASKS_FILE
        )


# =====================================
# TASK EXTRACTION
# =====================================

def extract_task(message):

    prompt = f"""
You are a semantic task extraction engine.

Convert the following Telegram message into a concise,
clean, actionable task.

Rules:
- Remove emotional text
- Remove greetings
- Remove filler words
- Keep actionable meaning
- Keep important context
- Make task concise
- Sound natural

Examples:

Input:
"Please buy milk and bread while coming"

Output:
"Buy milk and bread"

Input:
"Hey love ❤️ don't forget baby medicines"

Output:
"Buy baby medicines"

Message:
{message}

Reply ONLY with the task.
"""

    try:

        task = generate_reply(prompt).strip()

        return task

    except Exception:

        logger.exception(
            "extract_task failed [message=%s]",
            message
        )

        return message


# =====================================
# TASK HELPERS
# =====================================

def task_exists(task_message):

    tasks = load_tasks()

    for task in tasks:

        existing_message = task.get("message", "").lower()

        if existing_message == task_message.lower():

            return True

    return False


def add_task(task):

    tasks = load_tasks()

    task.setdefault("created_at", str(datetime.now()))
    task.setdefault("updated_at", str(datetime.now()))
    task.setdefault("status", "PENDING")
    task.setdefault("priority", "NORMAL")

    tasks.append(task)

    save_tasks(tasks)


def update_last_reminded(task_index):

    tasks = load_tasks()

    if task_index >= len(tasks):

        return

    tasks[task_index]["last_reminded"] = str(datetime.now())
    tasks[task_index]["updated_at"] = str(datetime.now())

    save_tasks(tasks)


# =====================================
# TASK COMPLETION
# =====================================

def complete_task(identifier):

    """
    Complete a task by index or text match.

    Args:
        identifier:
            int → complete by index
            str → complete by text match

    Returns:
        bool
    """

    tasks = load_tasks()

    updated = False

    if isinstance(identifier, int):

        if identifier < len(tasks):

            tasks[identifier]["status"] = "COMPLETED"
            tasks[identifier]["updated_at"] = str(datetime.now())

            updated = True

    elif isinstance(identifier, str):

        identifier_lower = identifier.lower()

        # Keyword aliases: map natural completion phrases to task types/items
        TYPE_ALIASES = {
            "GROCERY":  ["grocery", "groceries", "vegetables", "milk",
                         "bread", "food", "snacks", "shopping"],
            "MEDICAL":  ["medicine", "medicines", "medical", "tablet",
                         "tablets", "hospital", "pharmacy", "doctor"],
            "GENERAL":  ["general", "task", "work", "report", "done"],
        }

        for task in tasks:

            # Match against items (e.g. "milk", "medicines", "groceries")
            items = task.get("items", [])
            items_text = " ".join(items).lower()

            # Match against task type using aliases
            task_type = task.get("type", "").upper()
            type_aliases = TYPE_ALIASES.get(task_type, [task_type.lower()])

            # Match against legacy "message" field if present
            task_message = task.get("message", "").lower()

            matched = (
                # user text contains item name
                any(
                    item.lower() in identifier_lower
                    for item in items
                    if item.strip()
                )
                # item name contains user text keyword
                or any(
                    identifier_lower in item.lower()
                    for item in items
                    if item.strip()
                )
                # user text matches a type alias
                or any(
                    alias in identifier_lower
                    for alias in type_aliases
                )
                # legacy message field match
                or identifier_lower in task_message
            )

            if matched:

                task["status"] = "COMPLETED"
                task["updated_at"] = str(datetime.now())

                updated = True

    if updated:

        save_tasks(tasks)

    return updated


# =====================================
# PENDING TASKS
# =====================================

def get_pending_tasks():

    tasks = load_tasks()

    return [
        task for task in tasks
        if task.get("status") == "PENDING"
    ]


# =====================================
# CONTACTS
# =====================================

def load_contacts():

    if not os.path.exists(CONTACTS_FILE):

        return {}

    try:

        with open(CONTACTS_FILE, "r") as file:

            return json.load(file)

    except Exception:

        logger.exception(
            "load_contacts failed [file=%s]",
            CONTACTS_FILE
        )

        return {}
