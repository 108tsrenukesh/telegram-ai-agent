import logging

from semantic_task_engine import load_tasks

from entity_memory_engine import get_pending_entities

logger = logging.getLogger(__name__)


def build_conversation_context(chat_id, sender_name):

    active_tasks = []

    try:

        tasks = load_tasks()

        for task in tasks:

            if (
                task.get("from") == sender_name
                and
                task.get("status") == "PENDING"
            ):

                active_tasks.append(task)

    except Exception:

        logger.exception(
            "build_conversation_context: load_tasks failed "
            "[chat_id=%s sender=%s] — using empty task list",
            chat_id, sender_name
        )

    pending_entities = []

    try:

        pending_entities = get_pending_entities(chat_id)

    except Exception:

        logger.exception(
            "build_conversation_context: get_pending_entities failed "
            "[chat_id=%s sender=%s] — using empty entity list",
            chat_id, sender_name
        )

    return {
        "active_tasks": active_tasks,
        "pending_entities": pending_entities
    }
