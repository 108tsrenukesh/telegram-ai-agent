import json
import re

from deadline_engine import (
    extract_deadline
)

from datetime import datetime


TASK_FILE = "tasks.json"


def load_tasks():

    try:

        with open(
            TASK_FILE,
            "r"
        ) as file:

            return json.load(file)

    except Exception:

        return []


def save_tasks(tasks):

    with open(
        TASK_FILE,
        "w"
    ) as file:

        json.dump(
            tasks,
            file,
            indent=4
        )


def classify_task_type(text):

    lower = text.lower()

    grocery_keywords = [

        "milk",
        "chips",
        "oil",
        "rice",
        "curd",
        "groceries",
        "vegetables"

    ]

    medicine_keywords = [

        "medicine",
        "tablet",
        "hospital",
        "medical"

    ]

    if any(
        word in lower
        for word in grocery_keywords
    ):

        return "GROCERY"

    if any(
        word in lower
        for word in medicine_keywords
    ):

        return "MEDICAL"

    return "GENERAL"


def extract_items(text):

    separators = [",", "and"]

    normalized = text

    for sep in separators:

        normalized = normalized.replace(
            sep,
            "|"
        )

    items = []

    for item in normalized.split("|"):

        cleaned = item.strip()

        if len(cleaned) > 2:

            items.append(cleaned)

    return items


def create_semantic_task(

    message,
    sender,
    priority

):

    tasks = load_tasks()

    task_type = classify_task_type(
        message
    )

    items = extract_items(
        message
    )

    task = {

        "id": len(tasks) + 1,

        "type": task_type,

        "items": items,

        "notes": [],

        "deadline": extract_deadline(message),

        "from": sender,

        "priority": priority,

        "status": "PENDING",

        "created_at": str(
            datetime.now()
        )

    }

    tasks.append(task)

    save_tasks(tasks)

    return task