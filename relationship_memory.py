import json
import logging

from config import RELATIONSHIP_MEMORY_FILE as MEMORY_FILE

logger = logging.getLogger(__name__)


def load_relationship_memory():

    try:

        with open(MEMORY_FILE, "r") as file:

            return json.load(file)

    except FileNotFoundError:

        return {}

    except Exception:

        logger.exception(
            "load_relationship_memory failed [file=%s]",
            MEMORY_FILE
        )

        return {}


def save_relationship_memory(data):

    try:

        with open(MEMORY_FILE, "w") as file:

            json.dump(data, file, indent=4)

    except Exception:

        logger.exception(
            "save_relationship_memory failed [file=%s]",
            MEMORY_FILE
        )


def update_relationship_memory(person, topic):

    memory = load_relationship_memory()

    if person not in memory:

        memory[person] = {
            "topics": [],
            "interaction_count": 0
        }

    if topic not in memory[person]["topics"]:

        memory[person]["topics"].append(topic)

    memory[person]["interaction_count"] += 1

    save_relationship_memory(memory)
