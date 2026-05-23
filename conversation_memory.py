import json
import logging

from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

MEMORY_FILE = "conversation_state.json"


def load_memory():

    try:

        with open(MEMORY_FILE, "r") as file:

            return json.load(file)

    except FileNotFoundError:

        return {}

    except Exception:

        logger.exception(
            "load_memory failed [file=%s]",
            MEMORY_FILE
        )

        return {}


def save_memory(data):

    try:

        with open(MEMORY_FILE, "w") as file:

            json.dump(data, file, indent=4)

    except Exception:

        logger.exception(
            "save_memory failed [file=%s]",
            MEMORY_FILE
        )


def get_chat_state(chat_id):

    memory = load_memory()

    return memory.get(str(chat_id), {})


def update_chat_state(chat_id, state):

    memory = load_memory()

    state["active_until"] = (
        datetime.now() + timedelta(hours=1)
    ).isoformat()

    memory[str(chat_id)] = state

    save_memory(memory)


def clear_chat_state(chat_id):

    memory = load_memory()

    if str(chat_id) in memory:

        del memory[str(chat_id)]

    save_memory(memory)


def set_conversation_state(chat_id, state_name):

    memory = load_memory()

    if str(chat_id) not in memory:

        memory[str(chat_id)] = {}

    memory[str(chat_id)]["conversation_state"] = state_name

    memory[str(chat_id)]["active_until"] = (
        datetime.now() + timedelta(hours=2)
    ).isoformat()

    save_memory(memory)


def is_conversation_active(chat_id):

    state = get_chat_state(chat_id)

    active_until = state.get("active_until")

    if not active_until:

        return False

    try:

        expiry = datetime.fromisoformat(active_until)

        return datetime.now() < expiry

    except Exception:

        logger.exception(
            "is_conversation_active failed parsing expiry "
            "[chat_id=%s active_until=%s]",
            chat_id, active_until
        )

        return False
