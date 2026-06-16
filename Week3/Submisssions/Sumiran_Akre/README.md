# AI Research Assistant with n8n

An AI-powered research assistant built using **n8n**, **Groq LLM**, **Tavily Search**, and **Gmail**.

The workflow accepts a user's query through an n8n Chat Trigger, performs a web search using Tavily, generates a concise research summary with Groq's Llama 3.3 70B model, and emails the result automatically using Gmail.

---

## Workflow Overview

```text
User Chat
    │
    ▼
Chat Trigger
    │
    ▼
AI Agent
 ├── Groq Chat Model
 ├── Simple Memory
 └── Tavily Search Tool
    │
    ▼
Gmail
    │
    ▼
Research Summary Sent via Email
```

---

## Features

- 💬 Chat-based interface
- 🌐 Real-time web search using Tavily
- 🧠 Context-aware conversations with memory
- ⚡ Fast inference using Groq Llama 3.3 70B
- 📧 Automatically emails research summaries
- 🔍 Uses multiple web sources before answering

---

## Tech Stack

- **n8n**
- **Groq API**
- **Tavily Search API**
- **Gmail OAuth2**
- **Llama 3.3 70B Versatile**

---

## Workflow Components

### 1. Chat Trigger

Receives the user's message and starts the workflow.

---

### 2. AI Agent

Responsible for:

- Understanding the prompt
- Searching the web
- Summarizing findings
- Using conversation memory
- Preparing the email content

System Prompt:

> You are an expert research assistant.
>
> - Search the web before answering.
> - Read multiple sources.
> - Produce a concise summary.
> - Include important facts.
> - Mention source URLs.
> - Send the summary using Email.
> - Inform the user after sending.

---

### 3. Groq Chat Model

Model:

```
llama-3.3-70b-versatile
```

Used for reasoning and response generation.

---

### 4. Tavily Search

Configuration:

- Topic: General
- Search Depth: Advanced
- Max Results: 5

Provides recent and relevant web information.

---

### 5. Simple Memory

Maintains conversation context across messages for more coherent responses.

---

### 6. Gmail

Automatically sends the generated summary.

Email configuration:

- Subject = User's query
- Body = AI-generated summary

---

### Import Workflow

Open n8n

→ Import Workflow

→ Select

```
agent.json
```

---

### Configure Credentials

Create credentials for:

- Groq API
- Tavily API
- Gmail OAuth2

Attach them to the corresponding nodes.

---

## Required APIs

### Groq

Create an API key from

https://console.groq.com/

---

### Tavily

Create an API key from

https://app.tavily.com/

---

### Gmail OAuth

Create OAuth credentials inside Google Cloud Console and connect them in n8n.

---

## Example

### User

```
Explain Large Language Models
```

### AI

- Searches the web
- Reads multiple sources
- Creates a concise summary
- Emails the summary

---

## Screenshots

### Workflow

Add your workflow screenshot here.

### Execution

Add your execution screenshot here.

---

## Future Improvements

- PDF generation
- Multiple recipients
- Slack integration
- Telegram bot
- Citation formatting
- RAG with vector database
- Streaming responses
- Agentic workflows

---

## Project Structure

```
.
├── README.md
├── workflow
|    ├── agent.json
└── screenshots
    ├── diagram.png
    └── execution.png
```

