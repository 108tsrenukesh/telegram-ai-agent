def normalize_item(text):

    text = text.lower().strip()

    replacements = {

        "packet chips": "chips",
        "chips packet": "chips",
        "2l milk": "milk",
        "milk 2l": "milk"

    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new
        )

    return text


def merge_items(existing, new_items):

    normalized_existing = [

        normalize_item(item)
        for item in existing

    ]

    for item in new_items:

        cleaned = normalize_item(
            item
        )

        if cleaned not in normalized_existing:

            existing.append(cleaned)

            normalized_existing.append(
                cleaned
            )

    return existing