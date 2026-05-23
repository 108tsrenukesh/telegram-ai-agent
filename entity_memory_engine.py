import json


ENTITY_FILE = (
    "entity_memory.json"
)


def load_entity_memory():

    try:

        with open(
            ENTITY_FILE,
            "r"
        ) as file:

            return json.load(file)

    except Exception:

        return {}


def save_entity_memory(data):

    with open(
        ENTITY_FILE,
        "w"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )


def update_entity(

    chat_id,
    entity,
    status

):

    memory = (
        load_entity_memory()
    )

    chat_id = str(chat_id)

    if chat_id not in memory:

        memory[chat_id] = {}

    memory[chat_id][entity] = status

    save_entity_memory(memory)


def get_pending_entities(chat_id):

    memory = (
        load_entity_memory()
    )

    chat_id = str(chat_id)

    if chat_id not in memory:

        return []

    pending = []

    for entity, status in memory[
        chat_id
    ].items():

        if status != "COMPLETE":

            pending.append(entity)

    return pending


def complete_entity(

    chat_id,
    entity

):

    memory = (
        load_entity_memory()
    )

    chat_id = str(chat_id)

    if (
        chat_id in memory
        and
        entity in memory[chat_id]
    ):

        memory[chat_id][
            entity
        ] = "COMPLETE"

    save_entity_memory(memory)