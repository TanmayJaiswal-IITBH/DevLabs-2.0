# 🤖 Multi-Agent Research Crew using CrewAI

A simple **Multi-Agent AI workflow** built using **CrewAI** and **Groq LLM**. This project demonstrates how multiple AI agents collaborate sequentially to research a topic, write an article, and review the final content.

---

## 🚀 Features

* **Three Specialized AI Agents** working together.
* **Sequential Workflow** using `Process.sequential`.
* **Role-Based Task Delegation** where each agent has a specific responsibility.
* **Dynamic User Input** using `crew.kickoff(inputs={...})`.
* **Environment Variable Support** for secure API key management with `.env`.

---

## 🛠️ Technologies Used

* Python
* CrewAI
* LangChain Groq
* Groq LLM (`llama-3.3-70b-versatile`)
* Python Dotenv

---

## 🏗️ Project Architecture

```text
User Topic
     │
     ▼
Research Task
     │
     ▼
Researcher Agent
     │
     ▼
Writing Task
     │
     ▼
Writer Agent
     │
     ▼
Review Task
     │
     ▼
Reviewer Agent
     │
     ▼
Final Article
```

---

## 👥 Agents

### 🔍 Researcher

* Researches the given topic.
* Collects key facts, concepts, applications, advantages, and challenges.
* Passes the research findings to the Writer.

### ✍️ Writer

* Converts the research into a well-structured article.
* Organizes the content with proper flow and readability.
* Sends the draft to the Reviewer.

### 🧐 Reviewer

* Reviews the article for grammar, clarity, and completeness.
* Improves readability while preserving the original meaning.
* Produces the final polished article.

---

## 📋 Workflow

The project follows a **Sequential Process**:

```text
User Topic
     │
     ▼
Researcher
     │
     ▼
Writer
     │
     ▼
Reviewer
     │
     ▼
Final Output
```

---

## 📁 Project Structure

```text
.
├── agents.py
├── tasks.py
├── crew.py
├── main.py
├── .env
├── requirements.txt
└── README.md
```

---

## 📄 File Description

### `agents.py`

Creates the three AI agents (Researcher, Writer, and Reviewer) and configures the Groq LLM used by all agents.

### `tasks.py`

Defines the tasks assigned to each agent, including the task descriptions and expected outputs.

### `crew.py`

Builds the Crew by combining the agents and tasks and executes them using a sequential workflow.

### `main.py`

Acts as the entry point of the application. It accepts the topic from the user, starts the workflow using `crew.kickoff()`, and displays the final article.

### `.env`

Stores the Groq API key securely.

### `requirements.txt`

Lists the required Python packages for running the project.

---

## ▶️ How to Run

1. Clone the repository.

```bash
git clone <repository-url>
cd <repository-name>
```

2. Install the dependencies.

```bash
pip install -r requirements.txt
```

3. Create a `.env` file and add your API key.

```text
GROQ_API_KEY=your_groq_api_key
```

4. Run the project.

```bash
python main.py
```

---

## 🎯 Learning Outcomes

Through this project, the following concepts were implemented:

* CrewAI fundamentals
* Multi-Agent collaboration
* Role-based agent design
* Task creation and delegation
* Sequential workflow execution
* Passing dynamic inputs using `crew.kickoff()`
* Prompt engineering through task descriptions
* Environment variable management using `.env`
* Building a complete AI-powered workflow


## ⚠️ Version Compatibility

This project was developed and tested using the following package versions:

```text
crewai==0.130.0
langchain-groq==0.3.7
python-dotenv
```

> **Note:** Newer versions of CrewAI may introduce breaking changes or compatibility issues with `langchain-groq` and Groq models. If you encounter errors related to LLM initialization, tool execution, or API compatibility, it is recommended to use the versions listed above for the best experience.
