import json
import logging

from datetime import datetime

from deadline_engine import extract_deadline

from config import TASKS_FILE as TASK_FILE

logger = logging.getLogger(__name__)


def load_tasks():

    try:

        with open(TASK_FILE, "r") as file:

            return json.load(file)

    except FileNotFoundError:

        return []

    except Exception:

        logger.exception(
            "load_tasks failed [file=%s]",
            TASK_FILE
        )

        return []


def save_tasks(tasks):

    try:

        with open(TASK_FILE, "w") as file:

            json.dump(tasks, file, indent=4)

    except Exception:

        logger.exception(
            "save_tasks failed [file=%s]",
            TASK_FILE
        )


def classify_task_type(text):

    lower = text.lower()

    grocery_keywords = [
        "milk", "chips", "oil", "rice",
        "curd", "groceries", "vegetables"
    ]

    medicine_keywords = [
        "medicine", "tablet", "hospital", "medical"
    ]

    if any(word in lower for word in grocery_keywords):

        return "GROCERY"

    if any(word in lower for word in medicine_keywords):

        return "MEDICAL"

    return "GENERAL"


def extract_items(text):

    separators = [",", "and"]

    normalized = text

    for sep in separators:

        normalized = normalized.replace(sep, "|")

    items = []

    for item in normalized.split("|"):

        cleaned = item.strip()

        if len(cleaned) > 2:

            items.append(cleaned)

    return items


def create_semantic_task(message, sender, priority):

    tasks = load_tasks()

    task_type = classify_task_type(message)

    items = extract_items(message)

    task = {
        "id": len(tasks) + 1,
        "type": task_type,
        "items": items,
        "notes": [],
        "deadline": extract_deadline(message),
        "from": sender,
        "priority": priority,
        "status": "PENDING",
        "created_at": str(datetime.now())
    }

    tasks.append(task)

    save_tasks(tasks)

    return task
