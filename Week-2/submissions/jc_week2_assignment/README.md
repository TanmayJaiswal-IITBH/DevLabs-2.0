AI Tool Calling Agent using Anthropic Claude
📌 Overview

This project is a simple AI agent built from scratch using the Anthropic Claude API. Instead of using frameworks like LangChain or LangGraph, it manually implements the complete tool-calling workflow. The agent can perform addition, multiplication, and fetch live weather information by calling external Python functions.

🎯 Aim

The goal of this project is to understand how AI agents and LLM tool calling work internally by implementing the entire process manually.

🛠️ Technologies Used
Python
Anthropic Claude API
Pydantic
Requests
🚀 Features
Custom AI agent with tool calling
Input validation using Pydantic
Dynamic tool execution
Live weather API integration
Error handling and modular design
📚 What I Learned
Building an AI agent from scratch
Creating reusable tools using OOP
Validating inputs with Pydantic
Generating JSON schemas for LLM tools
Registering and executing tools dynamically
Managing the conversation flow between the LLM and external tools
Integrating external APIs and handling exceptions
🔄 Workflow
User Query
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
        Claude Final Answer
🌱 Future Improvements
Add conversation memory
Add more tools
Build a Streamlit interface
Support asynchronous tool execution
Improve logging and monitoring