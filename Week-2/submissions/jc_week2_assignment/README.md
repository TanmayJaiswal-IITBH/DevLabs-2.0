# 🤖 AI Tool Calling Agent using Anthropic Claude

A lightweight terminal-based AI Agent built using the **Anthropic Claude API**, **Pydantic V2**, and **Python**. This project demonstrates how to implement the complete tool-calling workflow from scratch without relying on frameworks like LangChain or LangGraph. The agent can reason over user queries, invoke external tools when required, validate inputs using Pydantic, and generate accurate responses using real-time tool outputs.

---

## 🚀 Features

* **Manual Tool Calling Workflow:** Implements the complete Claude tool-calling loop without any agent frameworks.
* **Pydantic V2 Input Validation:** Validates and sanitizes tool inputs before execution using custom `@field_validator`s.
* **Reusable Tool Architecture:** A generic `Tool` wrapper makes it easy to register and execute new tools.
* **Live Weather Integration:** Retrieves real-time weather information using the public **wttr.in** API.
* **Dynamic Tool Dispatch:** Claude automatically decides which tool to invoke based on the user's request.
* **Robust Error Handling:** Handles validation failures and API errors gracefully without crashing the application.

---

## 🛠️ Installation & Setup

1. **Clone the repository and install the dependencies:**

   ```bash
   pip install anthropic pydantic requests
   ```

2. **Configure your Anthropic API key:**

   Replace the placeholder inside the code:

   ```python
   anthropic.Anthropic(api_key="your_api_key")
   ```

3. **Run the application:**

   ```bash
   python main.py
   ```

---

## 🏗️ Core Architecture & Tool Design

The project uses a custom `Tool` abstraction that combines input validation, schema generation, and execution into a reusable component. Each tool exposes its input schema to Claude using Pydantic's `model_json_schema()`, allowing the model to understand when and how to call the tool.

| Tool Name | Input Schema | Backend Implementation | Description |
| :--- | :--- | :--- | :--- |
| `addition` | `a`, `b` | Python Function | Adds two positive integers after validating the inputs. |
| `multiplier` | `a`, `b` | Python Function | Multiplies two positive integers after validating the inputs. |
| `get_weather` | `city` | `wttr.in` API | Retrieves the current weather conditions for a specified city. |

---

## 🎯 Sample Executions

### Example 1: Addition

**User Query:**  
> Add 25 and 18.

**Agent Output:**  
> The sum of 25 and 18 is **43**.

---

### Example 2: Multiplication

**User Query:**  
> Multiply 12 and 15.

**Agent Output:**  
> 12 × 15 = **180**.

---

### Example 3: Weather Lookup

**User Query:**  
> What's the weather like in Hyderabad?

**Agent Output:**  
> Hyderabad: 🌤 +31°C

---

## 📚 Concepts Covered

- Anthropic Claude Tool Calling
- Function Calling with LLMs
- Pydantic V2 Data Validation
- Custom Field Validators
- JSON Schema Generation
- Object-Oriented Programming (OOP)
- Dynamic Tool Registration
- Conversation State Management
- External API Integration
- Exception Handling
- Modular Python Design

---

## 🔄 Workflow

```text
User Input
      │
      ▼
Agent
      │
      ▼
Claude API
      │
      ▼
Tool Request?
      │
 ┌────┴────┐
 │         │
No        Yes
 │         │
 ▼         ▼
Return   Validate Input
Answer        │
              ▼
      Execute Python Tool
              │
              ▼
      Return Tool Result
              │
              ▼
 Claude Generates Final Response
```

---

## 🚀 Future Improvements

- Add conversation memory for multi-turn chats.
- Support additional tools such as search, calculator, and file reader.
- Store API keys securely using environment variables.
- Build a Streamlit-based user interface.
- Add logging and monitoring.
- Support asynchronous tool execution.

---

## 📌 Conclusion

This project provides a hands-on understanding of how AI agents perform tool calling internally. By manually implementing the complete interaction loop between Claude and external Python tools, it builds a strong foundation for learning advanced agent frameworks such as LangChain and LangGraph while understanding the mechanics they abstract away.