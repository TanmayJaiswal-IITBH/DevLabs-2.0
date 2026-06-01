# FuelWise

FuelWise is a Week 1 AI agent submission for **DevLabs 2.0**.

It is a local mess-menu assistant for hostel students. The user asks what they should eat, and FuelWise uses tools to check the menu, nutrition, fitness goal, allergies, outside-food options, and dish ratings before giving a practical answer.

## Why I Built This

Hostel students make food decisions every day:

```text
Should I eat mess food, skip something, add protein, or order outside?
```

That decision depends on the menu, fitness goal, allergies, budget, and personal taste. FuelWise turns that confusion into a simple AI-agent workflow.

## What Makes It An Agent

FuelWise is not just a chatbot. It follows a basic ReAct-style flow:

```text
User asks -> Model chooses a tool -> Python runs the tool -> Model uses the result -> Final answer
```

The model runs locally through **Ollama**, so no paid API key is required.

## Tools

| Tool | Purpose |
|------|---------|
| `get_today_menu(meal)` | Shows today's breakfast, lunch, snacks, dinner, or full menu |
| `get_nutrition(dish)` | Shows calories, protein, carbs, fat, allergens, and notes |
| `check_user_goals(goal)` | Gives plate-building advice for bulk, cut, or maintain |
| `suggest_outside_alternative(craving, budget)` | Suggests outside food within budget |
| `log_meal_rating(dish, rating)` | Logs a 1-5 dish rating |

## Requirements

- Python 3.9+
- Ollama installed
- `llama3.2` model pulled once

No extra Python packages are needed. just ollama

## Quick Start

Go to this folder:

```bash
cd Week-1/submissions/Prakhar
```

Start Ollama:

```bash
ollama serve
```

If this shows `address already in use`, Ollama is already running. That is fine.

Open another terminal and pull the model:

```bash
ollama pull llama3.2
```

Run FuelWise:

```bash
python3 mess_menu_agent.py
```

For slower laptops, use the smaller model:

```bash
ollama pull llama3.2:1b
OLLAMA_MODEL=llama3.2:1b python3 mess_menu_agent.py
```

## Example Prompts

After running the script, type a prompt after `You:`.

```text
I am cutting. What should I eat for dinner today?
I want high protein food under Rs 120. What should I order?
I have a peanut allergy. Is today's breakfast safe?
I want to bulk. Build me a lunch plate.
Log Paneer Curry as 4 out of 5.
```

To stop:

```text
exit
```

## Expected Output

When FuelWise uses a tool, you will see logs like this:

```text
-> Calling: get_today_menu({'meal': 'dinner'})
<- Result: Monday mess menu:
```

Then the agent gives the final answer:

```text
Agent: For dinner, choose paneer curry with roti and cucumber salad...
```

This confirms that the model is calling tools instead of only generating text.

## Troubleshooting

If Ollama is not running:

```bash
ollama serve
```

If the model is missing:

```bash
ollama pull llama3.2
```

If the response is slow:

```bash
OLLAMA_MODEL=llama3.2:1b python3 mess_menu_agent.py
```

If Ollama is unavailable, the script still prints an offline tool preview so the project can be inspected.

## Files

```text
README.md
mess_menu_agent.py
```

## Future Scope

FuelWise can become a real campus tool by connecting the menu to a Google Sheet, sending daily recommendations through WhatsApp or Telegram, and using ratings to collect mess feedback.
