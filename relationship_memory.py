import json


MEMORY_FILE = (
    "relationship_memory.json"
)


def load_relationship_memory():

    try:

        with open(
            MEMORY_FILE,
            "r"
        ) as file:

            return json.load(file)

    except Exception:

        return {}


def save_relationship_memory(data):

    with open(
        MEMORY_FILE,
        "w"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )


def update_relationship_memory(

    person,
    topic

):

    memory = (
        load_relationship_memory()
    )

    if person not in memory:

        memory[person] = {

            "topics": [],
            "interaction_count": 0

        }

    if (
        topic
        not in memory[person]["topics"]
    ):

        memory[person]["topics"].append(
            topic
        )

    memory[person][
        "interaction_count"
    ] += 1

    save_relationship_memory(
        memory
    )