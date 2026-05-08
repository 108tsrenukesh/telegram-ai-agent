import json
import os


TASKS_FILE = "tasks.json"


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

def complete_task(task_index):

    tasks = load_tasks()

    if task_index < len(tasks):

        tasks[task_index][
            "status"
        ] = "COMPLETED"

        save_tasks(tasks)

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