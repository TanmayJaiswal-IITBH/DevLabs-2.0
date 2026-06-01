# 🎓 IIT Bhilai Campus Life AI Agent

**DevLabs 2.0 | Week 1 Assignment**  
**Domain:** Campus Life Assistant

---

## What is this?

**Campus Assistant** is a conversational AI agent for IIT Bhilai students, built using a local LLM (via Ollama) and a **ReAct loop** (Reason → Act → Observe).

The agent can answer three types of student queries using tool calls:

| Tool | What it does |
|------|-------------|
| `get_mess_menu` | Returns the mess menu and timings for any day |
| `get_club_info` | Gives details about campus clubs and upcoming events |
| `get_academic_deadlines` | Lists exam dates and assignment due dates by course |

---

## How it works

```
User Query
    ↓
LLM reasons about which tool to call   (REASON)
    ↓
Tool is executed with the right args    (ACT)
    ↓
Result is fed back into context         (OBSERVE)
    ↓
LLM produces a final friendly response
```

The agent loops until the model stops calling tools and returns a natural language answer.

---

## Setup & Run

### 1. Install dependencies
```bash
pip install ollama
```

### 2. Pull a model
```bash
ollama pull llama3.2
# Alternatives: llama3.1 | qwen2.5 | mistral-nemo
```

### 3. Run the agent
```bash
python agent.py
```

### Sample output
```
User: What's for dinner tonight?
  → Calling: get_mess_menu({'day': 'today'})
  ← Result: 📅 Mess Menu — Monday
             ...
Campus Assistant: Tonight's dinner is Paneer Butter Masala with Dal Tadka...

User: Tell me about OpenLake.
  → Calling: get_club_info({'club_name': 'OpenLake'})
  ← Result: 🏛 OpenLake — Open Source Community...
Campus Assistant: OpenLake is IIT Bhilai's open-source community...
```

---

## Sample Queries

```
"What's for dinner tonight?"
"Tell me about OpenLake and any upcoming events."
"When are my CS251 exams and assignments due?"
"What end-semester exams are coming up?"
```

---

## Project Structure

```
Priyanshu_Priyadarshi/
├── agent.py       # All tools + ReAct agent (single file)
└── README.md
```

---

## Why this domain?

Every IIT student has the same three recurring questions: *"What's in the mess?"*, *"What's the deadline?"*, and *"What's OpenLake doing?"* — this agent answers all three.
