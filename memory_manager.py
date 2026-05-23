import json
import os
from datetime import datetime

from ai_router import generate_reply


TASKS_FILE = "tasks.json"

CONTACTS_FILE = "contacts.json"


# =====================================
# TASK FILE HELPERS
# =====================================

def load_tasks():

    if not os.path.exists(
        TASKS_FILE
    ):

        return []

    try:

        with open(
            TASKS_FILE,
            "r"
        ) as file:

            return json.load(file)

    except Exception:

        return []


def save_tasks(tasks):

    try:

        with open(
            TASKS_FILE,
            "w"
        ) as file:

            json.dump(
                tasks,
                file,
                indent=4
            )

    except Exception:

        pass


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

        task = generate_reply(
            prompt
        ).strip()

        return task

    except Exception:

        return message


# =====================================
# TASK HELPERS
# =====================================

def task_exists(task_message):

    tasks = load_tasks()

    for task in tasks:

        existing_message = (
            task.get(
                "message",
                ""
            ).lower()
        )

        if (
            existing_message
            ==
            task_message.lower()
        ):

            return True

    return False


def add_task(task):

    tasks = load_tasks()

    task.setdefault(
        "created_at",
        str(datetime.now())
    )

    task.setdefault(
        "updated_at",
        str(datetime.now())
    )

    task.setdefault(
        "status",
        "PENDING"
    )

    task.setdefault(
        "priority",
        "NORMAL"
    )

    tasks.append(task)

    save_tasks(tasks)


def update_last_reminded(
    task_index
):

    tasks = load_tasks()

    if (
        task_index
        >=
        len(tasks)
    ):

        return

    tasks[task_index][
        "last_reminded"
    ] = str(
        datetime.now()
    )

    tasks[task_index][
        "updated_at"
    ] = str(
        datetime.now()
    )

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

    if isinstance(
        identifier,
        int
    ):

        if (
            identifier
            <
            len(tasks)
        ):

            tasks[identifier][
                "status"
            ] = "COMPLETED"

            tasks[identifier][
                "updated_at"
            ] = str(
                datetime.now()
            )

            updated = True

    elif isinstance(
        identifier,
        str
    ):

        for task in tasks:

            task_message = (
                task.get(
                    "message",
                    ""
                ).lower()
            )

            if (
                identifier.lower()
                in
                task_message
            ):

                task["status"] = (
                    "COMPLETED"
                )

                task["updated_at"] = str(
                    datetime.now()
                )

                updated = True

    if updated:

        save_tasks(tasks)

    return updated


# =====================================
# PENDING TASKS
# =====================================

def get_pending_tasks():

    tasks = load_tasks()

    pending = []

    for task in tasks:

        if (
            task.get("status")
            ==
            "PENDING"
        ):

            pending.append(task)

    return pending


# =====================================
# CONTACTS
# =====================================

def load_contacts():

    if not os.path.exists(
        CONTACTS_FILE
    ):

        return {}

    try:

        with open(
            CONTACTS_FILE,
            "r"
        ) as file:

            return json.load(file)

    except Exception:

        return {}