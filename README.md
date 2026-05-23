<div align="center">

```
██╗     ██╗   ██╗ ██████╗██╗███████╗███████╗██████╗
██║     ██║   ██║██╔════╝██║██╔════╝██╔════╝██╔══██╗
██║     ██║   ██║██║     ██║█████╗  █████╗  ██████╔╝
██║     ██║   ██║██║     ██║██╔══╝  ██╔══╝  ██╔══██╗
███████╗╚██████╔╝╚██████╗██║██║     ███████╗██║  ██║
╚══════╝ ╚═════╝  ╚═════╝╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝
```

### Persistent · Stateful · Relationship-Aware · Conversationally Intelligent

*A production-grade personal AI assistant built on Telegram — not a chatbot, but a cognitive orchestration system.*

---

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Bot_API-26A5E4?style=flat-square&logo=telegram&logoColor=white)
![Groq](https://img.shields.io/badge/LLM-Groq_LLaMA_3.3-FF6B35?style=flat-square)
![Gemini](https://img.shields.io/badge/Fallback-Gemini_2.5_Flash-4285F4?style=flat-square&logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)
![Status](https://img.shields.io/badge/Status-Production_Ready-22C55E?style=flat-square)

</div>

---

## What is Lucifer?

Lucifer is a **persistent conversational AI orchestration system** that acts as a real personal assistant over Telegram — not a simple autoresponder, not a command-driven bot.

It understands who you are talking to. It remembers what was said. It knows what is pending. It adapts its tone based on relationship. It asks for clarification when needed. It tracks tasks, resolves entities, schedules reminders, and generates emotionally intelligent replies — all in real-time, across conversations that span hours or days.

> **The core design goal:** Make AI behave like a trusted human assistant, not a machine responding to commands.

---

## Why Lucifer is Different

| Dimension | Traditional Chatbot | Lucifer |
|---|---|---|
| Memory | Stateless — each message is independent | Stateful — full conversation history persisted |
| Context | None — no awareness of prior messages | Grounded — active tasks, entities, relationships all inform replies |
| Task handling | Simple keyword matching | Semantic extraction, item merging, follow-up tracking |
| Tone | Uniform | Relationship-aware — wife, boss, friend, family each get different tone |
| Ambiguity | Ignores or errors | Detects and asks intelligent clarification questions |
| Reliability | Single LLM | Dual-LLM with automatic failover + template fallback |
| Corrections | Not handled | Full correction detection and task update workflow |

---

## System Architecture

```
╔══════════════════════════════════════════════════════════════════╗
║                     TELEGRAM INCOMING MESSAGE                    ║
╚══════════════════════════╦═══════════════════════════════════════╝
                           ║
                           ▼
         ┌─────────────────────────────────┐
         │    Conversation Window Engine   │  ← Groups fragmented messages
         │    conversation_window_engine   │    into natural conversational
         │                                 │    windows before processing
         └────────────────┬────────────────┘
                          │
                          ▼
         ┌─────────────────────────────────┐
         │        Intent Detection         │  ← Classifies intent:
         │         intent_engine           │    TASK / FOLLOWUP_TASK /
         │                                 │    CORRECTION / EMOTIONAL /
         └────────────────┬────────────────┘    CLOSURE / ACKNOWLEDGEMENT
                          │
              ┌───────────┼────────────┐
              ▼           ▼            ▼
    ┌──────────────┐ ┌──────────┐ ┌──────────────┐
    │   Clarif.    │ │ Context  │ │  Semantic    │
    │   Engine     │ │ Builder  │ │  Task Engine │
    │ (ambiguity?) │ │(grounding│ │(task extract,│
    │              │ │& memory) │ │ merge, store)│
    └──────┬───────┘ └────┬─────┘ └──────┬───────┘
           │              │               │
           └──────────────┼───────────────┘
                          │
                          ▼
         ┌─────────────────────────────────┐
         │    Conversation Phase Engine    │  ← Determines phase:
         │      conversation_phase         │    collecting / confirming /
         │                                 │    closing / emotional / normal
         └────────────────┬────────────────┘
                          │
                          ▼
         ┌─────────────────────────────────┐
         │      Entity Cognition Layer     │  ← Extracts and resolves
         │  entity_extractor +             │    unresolved conversational
         │  entity_memory_engine +         │    entities across turns
         │  entity_resolution_engine       │
         └────────────────┬────────────────┘
                          │
                          ▼
         ┌─────────────────────────────────┐
         │    Assistant Reply Generator    │  ← Relationship-aware,
         │   assistant_reply_generator     │    phase-sensitive, emotionally
         │                                 │    intelligent reply generation
         └────────────────┬────────────────┘
                          │
                          ▼
         ┌─────────────────────────────────┐
         │           AI Router             │  ← Groq (primary) →
         │           ai_router             │    Gemini (fallback) →
         │                                 │    Templates (final fallback)
         └────────────────┬────────────────┘
                          │
                          ▼
╔══════════════════════════════════════════════════════════════════╗
║                     TELEGRAM OUTGOING REPLY                      ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## Core Components — Deep Dive

### 1. AI Router (`ai_router.py`) — Dual-LLM with Failover

The AI Router is the backbone of every intelligent decision in the system. It implements a **three-tier fallback strategy** to guarantee a response even under complete LLM failure.

```
Request
   │
   ├──► GROQ (LLaMA 3.3 70B)  ──► Success? Return reply ✓
   │         [Primary]
   │         [Fails?]
   │              │
   ├──────────────►  Gemini 2.5 Flash  ──► Success? Return reply ✓
   │                    [Secondary]
   │                    [Fails?]
   │                         │
   └─────────────────────────►  Template Fallback  ──► Return reply ✓
                                   [Always available]
```

Every intelligent function in the system — intent detection, task extraction, clarification, entity resolution, reply generation — routes through this layer. Zero single points of failure.

---

### 2. Conversation Window Engine (`conversation_window_engine.py`) — Human Texting Awareness

Humans don't send one clean message. They send bursts.

```
Raw Telegram stream:
   "hey"
   "are you there"
   "add milk to the list"
   "and also bread"
   "oh and eggs too"

Without windowing → 5 separate intents processed independently
With windowing    → Grouped into 2 windows: greeting + grocery task
```

The engine uses LLM reasoning to group semantically connected messages into unified conversational windows before any intent detection or task extraction occurs.

---

### 3. Intent Detection Engine (`intent_engine.py`) — 9-Class Classification

Every incoming message is classified into one of nine intent categories:

| Intent | Description | Example |
|---|---|---|
| `TASK` | Action requested of Renukesh | *"Buy medicines on the way home"* |
| `FOLLOWUP_TASK` | Extension of existing task | *"Add chips also"* |
| `CORRECTION` | User disputes prior record | *"I never said milk"* |
| `TASK_COMPLETION` | Confirms task done | *"Done, bought everything"* |
| `STATUS_CHECK` | Asking for availability/status | *"Where are you right now?"* |
| `EMOTIONAL` | Affective message | *"Love you ❤️"* |
| `ACKNOWLEDGEMENT` | Simple reaction | *"Okay", "👍", "Thanks"* |
| `CLOSURE` | Conversation ending | *"Bye", "Good night"* |
| `GENERAL` | Everything else | General conversation |

Classification is LLM-driven with a defined allowed-set guard — invalid classifications fall back to `GENERAL`.

---

### 4. Semantic Task Engine (`semantic_task_engine.py`) — Structured Task Cognition

Tasks are not stored as raw strings. Every task is extracted, classified, and structured into a rich object:

```json
{
    "id": 4,
    "type": "GROCERY",
    "items": ["milk 2L", "bread", "baby diapers"],
    "notes": [],
    "deadline": "2026-05-23T20:00:00",
    "from": "Wife",
    "priority": "URGENT",
    "status": "PENDING",
    "created_at": "2026-05-23T17:45:00"
}
```

**Task type classification** uses keyword-based domain detection:

```
"milk", "chips", "oil", "rice", "curd", "groceries", "vegetables"  →  GROCERY
"medicine", "tablet", "hospital", "medical"                         →  MEDICAL
everything else                                                      →  GENERAL
```

**Item extraction** handles natural language separators:

```
Input:  "bring milk, bread and baby diapers"
Output: ["milk", "bread", "baby diapers"]
```

---

### 5. Deadline Engine (`deadline_engine.py`) — Natural Language Time Parsing

Deadline extraction converts natural language time references into ISO 8601 timestamps:

```
"call me at 7 PM"     →  2026-05-23T19:00:00  (today, or tomorrow if passed)
"tomorrow"            →  2026-05-24T09:00:00  (next day at 9 AM)
"tonight"             →  2026-05-23T20:00:00  (today at 8 PM)
```

Smart rollover: if a specified time has already passed today, it schedules for tomorrow automatically.

---

### 6. Clarification Engine (`clarification_engine.py`) — Ambiguity Detection

Before creating a task, Lucifer checks whether the message has enough information to act on.

```
Message: "bring medicines"
  │
  ▼
needs_clarification() → YES (no specific medicine named)
  │
  ▼
generate_clarification_reply() → "Sure ❤️ Which medicines should I note down?"

────────────────────────────────────────

Message: "bring Crocin and Dolo 650"
  │
  ▼
needs_clarification() → NO (specific items named)
  │
  ▼
Proceed to task creation directly
```

---

### 7. Entity Cognition Layer (`entity_extractor.py`, `entity_memory_engine.py`, `entity_resolution_engine.py`)

Entities are conversational objects that require tracking across multiple turns.

```
Turn 1:  "bring vegetables"
         → Entity: "vegetables" → Status: MISSING_DETAILS

Turn 2:  "spinach, tomatoes and potatoes"
         → Entity: "vegetables" → Status: COMPLETE
         → Task updated with resolved items
```

**Three-file architecture:**

```
entity_extractor.py       ← Identifies entities and their completeness status
entity_memory_engine.py   ← Persists entity state per chat_id in entity_memory.json
entity_resolution_engine  ← Detects which pending entities are resolved by new messages
```

---

### 8. Context Builder (`context_builder.py`) — Memory-Grounded Replies

Before generating any reply, Lucifer assembles a context object from live memory:

```python
context = {
    "active_tasks": [
        # All PENDING tasks from this sender
    ],
    "pending_entities": [
        # All unresolved entities for this chat_id
    ]
}
```

This context is injected into every reply generation prompt, dramatically reducing hallucinations. The LLM knows what is already pending, what has been asked, and what still needs resolution.

---

### 9. Conversation Phase Engine (`conversation_phase.py`) — Reply Calibration

Replies are calibrated differently depending on the detected conversational phase:

| Phase | Trigger | Reply Behaviour |
|---|---|---|
| `collecting` | TASK intent | Ask concise clarification, gather details |
| `confirming` | FOLLOWUP_TASK intent | Briefly acknowledge, minimal repetition |
| `closing` | Closure keywords detected | Warm short reply, do NOT recap tasks |
| `emotional` | Love/affection signals | Emotionally warm, relationship-appropriate |
| `normal` | Default | Standard contextual response |

---

### 10. Assistant Reply Generator (`assistant_reply_generator.py`) — Relationship-Sensitive Generation

The final reply is generated with full awareness of relationship, intent, phase, and conversation context.

**Relationship-to-tone mapping:**

```
Wife   →  Warm, emotionally intelligent, caring, concise, uses ❤️
Boss   →  Professional, efficient, respectful, no emojis
Friend →  Casual, relaxed, playful
Family →  Supportive, familiar, warm
```

**Phase-based length calibration:**

```
collecting  →  Short question only
confirming  →  Brief acknowledgement (one sentence max for wife)
closing     →  Warm but no task recap
emotional   →  Match the emotional register of the message
```

---

### 11. Reminder Intelligence (`reminder_scheduler.py`) — Priority-Based Scheduling

```
CRITICAL priority  →  Remind in 1 hour
URGENT priority    →  Remind in 1 hour
NORMAL priority    →  Remind in 2 hours
```

Reminder timing is anchored to `created_at` so urgency escalation is predictable and consistent.

---

### 12. Relationship & Conversation Memory (`relationship_memory.py`, `conversation_memory.py`)

**Relationship Memory** tracks per-person interaction history:

```json
{
    "Wife": {
        "topics": ["groceries", "medicines", "school fees"],
        "interaction_count": 47
    }
}
```

**Conversation State** manages per-chat active windows with TTL:

```
update_chat_state()     ← Sets 1-hour active window
set_conversation_state() ← Extends to 2-hour window
is_conversation_active() ← Checks if conversation is still live
clear_chat_state()      ← Clears on closure
```

---

## Memory Architecture

Lucifer uses a **JSON-based persistent state system** across five data stores:

```
memory/
├── tasks.json               ← Semantic tasks (structured, typed, prioritized)
├── conversation_state.json  ← Per-chat state, active window TTL
├── relationship_memory.json ← Per-person interaction history and topics
├── entity_memory.json       ← Per-chat entity resolution status
└── pending_replies.json     ← Reply queue
```

Each store is read-write on every relevant operation. No external database required. State survives process restarts.

---

## Complete Conversation Flows

### Flow 1 — Grocery Task with Follow-Ups

```
Wife:    Bring groceries

Lucifer: Sure ❤️ What all should I add to the list?

         [needs_clarification → YES]
         [generate_clarification_reply called]

Wife:    Milk and bread

         [Intent: FOLLOWUP_TASK]
         [items extracted: ["milk", "bread"]]
         [task created: GROCERY / PENDING]

Lucifer: Got it ❤️ I'll remind Renukesh.

Wife:    Add snacks also

         [Intent: FOLLOWUP_TASK]
         [task_merge_engine merges "snacks" into existing task]
         [items: ["milk", "bread", "snacks"]]

Lucifer: Done ❤️ Added snacks to the list.
```

---

### Flow 2 — Correction Handling

```
Wife:    I never said milk

         [Intent: CORRECTION]
         [conversation_phase → normal]

Lucifer: Oops ❤️ Got it, I'll remove milk from the list.

         [Task updated: milk removed from items]
```

---

### Flow 3 — Emotional + Closure

```
Wife:    Love you ❤️

         [Intent: EMOTIONAL]
         [phase: emotional]
         [relationship: Wife]

Lucifer: Aww ❤️ I'll pass that on to Renukesh.
         ❤️ Love you ! Bangaru Chinni..!

Wife:    Good night

         [Intent: CLOSURE]
         [phase: closing]
         [clear_chat_state() called]

Lucifer: Good night ❤️ Rest well.
```

---

### Flow 4 — Task with Deadline

```
Boss:    Send me the report by 6 PM today

         [Intent: TASK]
         [deadline_engine: "6 PM" → 2026-05-23T18:00:00]
         [task created: GENERAL / URGENT]
         [reminder scheduled: in 1 hour]

Lucifer: Understood. I'll make sure Renukesh gets this by 6 PM.
```

---

### Flow 5 — Ambiguous Medical Request

```
Friend:  Remind Renukesh to get medicines

         [Intent: TASK]
         [needs_clarification → YES — no medicine names]

Lucifer: Sure, which medicines should I note down?

Friend:  Crocin 500mg and some vitamin C

         [Intent: FOLLOWUP_TASK]
         [items: ["Crocin 500mg", "vitamin C"]]
         [type: MEDICAL / PENDING]

Lucifer: Got it, noted. I'll remind Renukesh about the medicines.
```

---

## Project Structure

```
telegram-ai-agent/
│
├── main.py                      ← Entry point — Telegram event loop, message orchestration
│
├── ai_router.py                 ← Dual-LLM routing (Groq → Gemini → Templates)
│
├── intent_engine.py             ← 9-class intent classification
│
├── semantic_task_engine.py      ← Task creation, classification, item extraction
│
├── clarification_engine.py      ← Ambiguity detection and clarification reply generation
│
├── conversation_window_engine.py ← Groups fragmented Telegram messages into windows
│
├── context_builder.py           ← Assembles memory-grounded context before reply
│
├── conversation_memory.py       ← Per-chat state management with TTL windows
│
├── conversation_phase.py        ← Detects conversational phase for reply calibration
│
├── assistant_reply_generator.py ← Relationship + phase-aware reply generation
│
├── entity_extractor.py          ← Extracts unresolved conversational entities
│
├── entity_memory_engine.py      ← Persists entity state per chat_id
│
├── entity_resolution_engine.py  ← Detects when pending entities are resolved
│
├── relationship_memory.py       ← Tracks per-person interaction history and topics
│
├── memory_manager.py            ← Task CRUD operations (load, save, complete, add)
│
├── deadline_engine.py           ← Natural language deadline extraction and parsing
│
├── reminder_scheduler.py        ← Priority-based reminder timing calculation
│
├── item_extractor.py            ← Semantic item extraction from natural language
│
├── task_merge_engine.py         ← Normalizes and merges follow-up task items
│
├── daily_summary.py             ← Generates pending/completed task daily summary
│
├── daily_brain.py               ← Extended brain summary with relationship insights
│
├── templates.py                 ← Fallback reply templates
│
├── tasks.json                   ← Persistent task store
├── conversation_state.json      ← Per-chat conversation state
├── relationship_memory.json     ← Per-person interaction memory
├── entity_memory.json           ← Entity resolution state
├── pending_replies.json         ← Reply queue
├── contacts.json                ← Contact-to-relationship mapping
│
└── requirements.txt             ← All dependencies
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Messaging | Telegram + Telethon | Client-side message streaming |
| Bot API | python-telegram-bot | Bot-side response dispatch |
| Primary LLM | Groq / LLaMA 3.3 70B | Low-latency inference |
| Secondary LLM | Gemini 2.5 Flash | Failover intelligence |
| Memory | JSON state files | Persistent multi-layer memory |
| Scheduling | Python asyncio | Async message handling |
| Deployment | GitHub Actions / local cron | Automated operation |

---

## Installation

### Prerequisites

- Python 3.8+
- A Telegram account
- Groq API key ([console.groq.com](https://console.groq.com))
- Gemini API key ([ai.google.dev](https://ai.google.dev))
- Telegram API credentials ([my.telegram.org](https://my.telegram.org))

### Setup

```bash
# Clone the repository
git clone https://github.com/108tsrenukesh/telegram-ai-agent.git
cd telegram-ai-agent

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_SESSION_STRING=your_session_string
TELEGRAM_BOT_TOKEN=your_bot_token
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
```

### Initialize State Files

```bash
echo "[]" > tasks.json
echo "{}" > conversation_state.json
echo "{}" > relationship_memory.json
echo "{}" > entity_memory.json
echo "[]" > pending_replies.json
```

### Run

```bash
python main.py
```

---

## Deployment Options

### Option 1 — Local with Auto-Restart

```bash
# Using nohup for persistent background execution
nohup python main.py > lucifer.log 2>&1 &
```

### Option 2 — GitHub Actions (Recommended for 24/7)

```yaml
name: Lucifer Assistant
on:
  schedule:
    - cron: '*/10 * * * *'   # Every 10 minutes
  workflow_dispatch:

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: python main.py
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          TELEGRAM_SESSION_STRING: ${{ secrets.TELEGRAM_SESSION_STRING }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
```

### Option 3 — Raspberry Pi / VPS

```bash
# systemd service for persistent operation
sudo nano /etc/systemd/system/lucifer.service

[Unit]
Description=Lucifer AI Assistant
After=network.target

[Service]
WorkingDirectory=/home/pi/telegram-ai-agent
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target

sudo systemctl enable lucifer
sudo systemctl start lucifer
```

---

## Daily Intelligence Reports

### Daily Summary (`daily_summary.py`)

```
📋 Daily Summary

✅ Completed: 3
📌 Pending: 5

Pending Tasks:
- GROCERY (URGENT)
- MEDICAL (NORMAL)
- GENERAL (URGENT)
```

### Brain Summary (`daily_brain.py`)

```
🧠 Lucifer Daily Brain

Pending Tasks: 5
Completed Tasks: 3

📌 Relationship Insights:

- Wife: 47 interactions
  Topics: groceries, medicines, school fees
- Boss: 12 interactions
  Topics: report, deadline, meeting

⚠️ Important Pending:

- [URGENT] GROCERY: milk, bread, snacks
- [NORMAL] MEDICAL: Crocin, vitamin C
```

---

## Current Capabilities

| Capability | Status | Engine |
|---|---|---|
| Dual-LLM with automatic failover | ✅ | `ai_router.py` |
| Semantic task cognition | ✅ | `semantic_task_engine.py` |
| 9-class intent classification | ✅ | `intent_engine.py` |
| Conversation window grouping | ✅ | `conversation_window_engine.py` |
| Ambiguity detection & clarification | ✅ | `clarification_engine.py` |
| Relationship-aware tone adaptation | ✅ | `assistant_reply_generator.py` |
| Conversational phase detection | ✅ | `conversation_phase.py` |
| Entity extraction & resolution | ✅ | `entity_extractor/memory/resolution` |
| Memory-grounded context building | ✅ | `context_builder.py` |
| Natural language deadline parsing | ✅ | `deadline_engine.py` |
| Task merge for follow-ups | ✅ | `task_merge_engine.py` |
| Correction detection & handling | ✅ | `intent_engine.py` + `main.py` |
| Priority-based reminder scheduling | ✅ | `reminder_scheduler.py` |
| Emotional conversation handling | ✅ | `conversation_phase.py` |
| Per-chat persistent state with TTL | ✅ | `conversation_memory.py` |
| Relationship & topic memory | ✅ | `relationship_memory.py` |
| Daily summaries & brain reports | ✅ | `daily_summary.py` / `daily_brain.py` |
| Semantic item extraction | ✅ | `item_extractor.py` |
| Template fallback guarantee | ✅ | `templates.py` |

---

## Roadmap

### Phase 2 — Multimodal Intelligence

- Voice note transcription and understanding
- Image and screenshot reasoning (OCR)
- Prescription and medical document parsing
- Invoice and receipt extraction

### Phase 3 — Predictive Intelligence

- Behavioral pattern learning
- Proactive reminder suggestions before asked
- Habit recognition across interaction history
- Predictive task creation from context signals

### Phase 4 — Autonomous Assistant Layer

- Calendar awareness and meeting preparation
- Autonomous follow-up scheduling
- Personal knowledge graph construction
- Deadline escalation with adaptive urgency

---

## Design Philosophy

Lucifer is built around a single core principle: **continuity over convenience**.

Most AI systems optimize for the single-turn interaction — one question, one answer. Lucifer is designed for the reality of human communication: fragmented, emotional, context-dependent, and ongoing.

Every architectural decision reflects this:

- **Memory over statelessness** — State is preserved, not discarded
- **Context over keywords** — Meaning is inferred, not matched
- **Relationship over uniformity** — Tone adapts to who is speaking
- **Clarification over assumption** — Ambiguity is surfaced, not silently ignored
- **Reliability over performance** — Three-tier failover before any silent error

---

## Author

Built by **T S Renukesh**

Iterative conversational AI architecture design and orchestration experimentation.

---

<div align="center">

*Lucifer is not a chatbot. It is a persistent cognitive system designed to function as a real personal assistant — one that remembers, adapts, and reasons across time.*

</div>
