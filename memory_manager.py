import json
import os
from ai_router import generate_reply
from datetime import datetime

TASKS_FILE = "tasks.json"


def update_last_reminded(
    task_index
):

    tasks = load_tasks()

    tasks[task_index][
        "last_reminded"
    ] = str(
        datetime.now()
    )

    save_tasks(tasks)

def complete_task(identifier):

    """
    Complete a task by index (int) or by matching text (str).

    Args:
        identifier: int → complete by index position
                    str → complete by matching task message content
    Returns:
        bool → True if at least one task was updated, False otherwise
    """

    tasks = load_tasks()

    updated = False

    if isinstance(identifier, int):

        if identifier < len(tasks):

            tasks[identifier]["status"] = "COMPLETED"

            updated = True

    elif isinstance(identifier, str):

        for task in tasks:

            if (
                identifier.lower()
                in
                task.get("message", "").lower()
            ):

                task["status"] = "COMPLETED"

                updated = True

    if updated:

        save_tasks(tasks)

    return updated

def task_exists(task_message):

    tasks = load_tasks()

    for task in tasks:

        if (
            task["message"].lower()
            ==
            task_message.lower()
        ):

            return True

    return False

def load_tasks():

    if not os.path.exists(
        TASKS_FILE
    ):

        return []

    with open(
        TASKS_FILE,
        "r"
    ) as file:

        return json.load(file)

def extract_task(message):

    prompt = f"""
Convert this Telegram message into a clean actionable task.

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



def save_tasks(tasks):

    with open(
        TASKS_FILE,
        "w"
    ) as file:

        json.dump(
            tasks,
            file,
            indent=4
        )

def get_pending_tasks():

    tasks = load_tasks()

    pending = []

    for task in tasks:

        if task["status"] == "PENDING":

            pending.append(task)

    return pending

CONTACTS_FILE = "contacts.json"


def load_contacts():

    if not os.path.exists(
        CONTACTS_FILE
    ):

        return {}

    with open(
        CONTACTS_FILE,
        "r"
    ) as file:

        return json.load(file)

def add_task(task):

    tasks = load_tasks()

    tasks.append(task)

    save_tasks(tasks)