from semantic_task_engine import (
    load_tasks
)

from entity_memory_engine import (
    get_pending_entities
)


def build_conversation_context(

    chat_id,
    sender_name

):

    tasks = load_tasks()

    active_tasks = []

    for task in tasks:

        if (
            task.get("from")
            == sender_name
            and
            task.get("status")
            == "PENDING"
        ):

            active_tasks.append(task)

    pending_entities = (
        get_pending_entities(
            chat_id
        )
    )

    context = {

        "active_tasks":
        active_tasks,

        "pending_entities":
        pending_entities

    }

    return context