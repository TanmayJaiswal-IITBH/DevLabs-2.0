# Research Assistant using LangGraph

## Objective

This project demonstrates how to build a Research Assistant using LangGraph. The assistant performs web-based research, maintains conversation memory, and requests human approval before revealing the generated summary.

## Features

* Stateful agent execution using LangGraph
* Persistent conversation memory using `SqliteSaver`
* Human-in-the-loop approval using `interrupt()` and `Command(resume=...)`
* Wikipedia search for factual information
* DuckDuckGo search for additional web results
* AI-generated research summaries

## Technologies Used

* Python
* LangGraph
* LangChain
* Groq (Llama 3.3 70B)
* SQLite
* Requests

## Project Structure

```text
.
├── app.py
├── graph.py
├── memory.py
├── requirements.txt
├── README.md
└── .env
```

## Installation

Clone the repository.

```bash
git clone <repository-url>
cd <repository-name>
```

Install the required packages.

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project directory and add your Groq API key.

```text
GROQ_API_KEY=your_api_key_here
```

## Running the Project

Run the application using:

```bash
python app.py
```

## Example Workflow

```text
User Question
      │
      ▼
LLM
      │
      ▼
Wikipedia Search
      │
      ▼
DuckDuckGo Search (if required)
      │
      ▼
Summary Generation
      │
      ▼
Human Approval
      │
      ▼
Display Summary
```

## Learning Outcomes

This project demonstrates the following LangGraph concepts:

* Stateful agent workflows
* Tool calling
* Persistent memory using SqliteSaver
* Human-in-the-loop execution
* Interrupt and resume functionality
* Multi-tool integration
