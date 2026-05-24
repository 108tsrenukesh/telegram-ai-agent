# =====================================
# LUCIFER — SHARED UTILITIES
# =====================================
# Common helpers used across multiple
# modules. Import from here — never
# duplicate logic in individual files.

import logging

logger = logging.getLogger(__name__)


def strip_json_fences(text):

    """
    Strip markdown code fences that LLMs sometimes wrap JSON output in.

    Handles:
        ```json ... ```
        ``` ... ```
        ` ... ` (single backtick edge case)

    Returns clean text ready for json.loads().
    """

    text = text.strip()

    if not text.startswith("`"):
        return text

    lines = text.splitlines()

    # Remove opening fence line (```json, ```JSON, ```, `)
    if lines and lines[0].startswith("`"):
        lines = lines[1:]

    # Remove closing fence line
    if lines and lines[-1].strip().startswith("`"):
        lines = lines[:-1]

    cleaned = "\n".join(lines).strip()

    if not cleaned:
        logger.warning(
            "strip_json_fences: result empty after stripping "
            "[original_length=%d]",
            len(text)
        )

    return cleaned
