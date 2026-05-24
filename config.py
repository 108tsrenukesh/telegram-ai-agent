# =====================================
# LUCIFER — CENTRAL CONFIGURATION
# =====================================
# All constants defined here.
# Import from this module everywhere —
# never hardcode values in other files.

# ── File paths ────────────────────────
TASKS_FILE               = "tasks.json"
CONTACTS_FILE            = "contacts.json"
CONVERSATION_STATE_FILE  = "conversation_state.json"
ENTITY_MEMORY_FILE       = "entity_memory.json"
RELATIONSHIP_MEMORY_FILE = "relationship_memory.json"
PENDING_REPLIES_FILE     = "pending_replies.json"
PROCESSED_MESSAGES_FILE  = "processed_messages.json"

# ── LLM settings ─────────────────────
LLM_MAX_RETRIES          = 3    # Attempts before falling back
LLM_LOG_TRUNCATE         = 200  # Max chars logged from LLM response
