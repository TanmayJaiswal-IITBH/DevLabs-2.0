"""
Budget Tracker Agent
An agent that helps you log expenses, check spending by category,
compare against monthly limits, and get a full summary.
"""
import ollama
from datetime import datetime
EXPENSES: list[dict] = []
BUDGET_LIMITS: dict[str, int] = {"food":8000,"transport":3000,"entertainment": 4000,"shopping":6000,"health":3000,"utilities":5000,"other":2000,}
VALID_CATEGORIES = list(BUDGET_LIMITS.keys())
# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def _this_month_expenses(category: str) -> list[dict]:
    """Return only expenses logged in the current calendar month."""
    prefix = datetime.now().strftime("%Y-%m")
    return [
        e for e in EXPENSES
        if e["category"] == category and e["date"].startswith(prefix)
    ]
# ─────────────────────────────────────────────
# TOOLS
# ─────────────────────────────────────────────
def log_expense(amount: int, category: str, description: str) -> str:
    """Log a new expense entry."""
    if not isinstance(amount, int) or amount <= 0:
        return "Invalid amount. Please provide a positive whole number in INR."

    category = category.lower().strip()
    if category not in VALID_CATEGORIES:
        return (
            f"Invalid category '{category}'. "
            f"Choose from: {', '.join(VALID_CATEGORIES)}."
        )
    entry = {
        "id": len(EXPENSES) + 1,
        "amount": amount,
        "category": category,
        "description": description,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    EXPENSES.append(entry)
    return f"Logged Rs.{amount:,} under '{category}' — {description}. (Entry #{entry['id']})"
def get_category_total(category: str) -> str:
    """Return total spent in a category this month."""
    category = category.lower().strip()
    if category not in VALID_CATEGORIES:
        return (
            f"Invalid category '{category}'. "
            f"Choose from: {', '.join(VALID_CATEGORIES)}."
        )
    total = sum(e["amount"] for e in _this_month_expenses(category))
    limit = BUDGET_LIMITS[category]
    remaining = limit - total
    pct = int((total / limit) * 100) if limit else 0
    status = "on track"
    if pct >= 100:
        status = "OVER BUDGET"
    elif pct >= 80:
        status = "nearing limit"
    return (
        f"[{category.upper()}] Spent Rs.{total:,} of Rs.{limit:,} limit "
        f"({pct}% used) — {status}. "
        f"Rs.{max(remaining, 0):,} remaining."
    )
def check_budget_limit(category: str) -> str:
    """Check whether a category is over, near, or within its limit."""
    category = category.lower().strip()
    if category not in VALID_CATEGORIES:
        return f"Unknown category '{category}'."
    total = sum(e["amount"] for e in _this_month_expenses(category))
    limit = BUDGET_LIMITS[category]
    pct = int((total / limit) * 100) if limit else 0
    if pct >= 100:
        return f"{category} is OVER BUDGET by Rs.{total - limit:,}."
    if pct >= 80:
        return (
            f"{category} is at {pct}% of limit. "
            f"Only Rs.{limit - total:,} left — spend carefully."
        )
    return f"{category} is fine — {pct}% used, Rs.{limit - total:,} available."
def get_spending_summary() -> str:
    """Return a full summary of all categories for the current month."""
    prefix = datetime.now().strftime("%Y-%m")
    month_expenses = [e for e in EXPENSES if e["date"].startswith(prefix)]
    if not month_expenses:
        return "No expenses logged yet this month."
    lines = ["Monthly Spending Summary\n"]
    total_spent = 0
    total_budget = sum(BUDGET_LIMITS.values())
    for cat, limit in BUDGET_LIMITS.items():
        spent = sum(e["amount"] for e in month_expenses if e["category"] == cat)
        total_spent += spent
        pct = int((spent / limit) * 100) if limit else 0
        flag = " [OVER]" if pct >= 100 else (" [WARN]" if pct >= 80 else "")
        lines.append(
            f"  {cat:<14} {pct:>3}%  Rs.{spent:>6,} / Rs.{limit:,}{flag}"
        )
    lines.append(
        f"\n  Total spent: Rs.{total_spent:,} of Rs.{total_budget:,} "
        f"({int((total_spent / total_budget) * 100)}%)"
    )
    return "\n".join(lines)
# ─────────────────────────────────────────────
# TOOL REGISTRY
# ─────────────────────────────────────────────
TOOL_FUNCTIONS = {
    "log_expense":          log_expense,
    "get_category_total":   get_category_total,
    "check_budget_limit":   check_budget_limit,
    "get_spending_summary": get_spending_summary,
}
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "log_expense",
            "description": (
                "Log a new expense. The function will automatically warn if the "
                "category is at 80%+ or over the monthly limit."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "amount":      {"type": "integer", "description": "Amount in INR, as a positive whole number"},
                    "category":    {"type": "string",  "description": f"One of: {', '.join(VALID_CATEGORIES)}"},
                    "description": {"type": "string",  "description": "Short note about what the expense was for"},
                },
                "required": ["amount", "category", "description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_category_total",
            "description": "Get the total amount spent in a category this month and how much of the limit is used.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": f"One of: {', '.join(VALID_CATEGORIES)}"},
                },
                "required": ["category"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_budget_limit",
            "description": "Check whether spending in a category is over, nearing, or within the monthly limit.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": f"One of: {', '.join(VALID_CATEGORIES)}"},
                },
                "required": ["category"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_spending_summary",
            "description": "Get a full month-to-date spending summary across all categories.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]
# ─────────────────────────────────────────────
# AGENT — ReAct loop
# ─────────────────────────────────────────────
class BudgetAgent:
    def __init__(self, model="llama3.1"):
        self.model = model
        self.system = (
            "You are a friendly personal finance assistant. "
            "Help the user track their monthly expenses against their budget limits. "
            "Categories available: " + ", ".join(VALID_CATEGORIES) + ". "
            "Budget warnings are built into log_expense — relay them clearly to the user. "
            "When asked for a summary or overview, use get_spending_summary. "
            "Be concise, supportive, and practical."
        )
    def run(self, user_message: str) -> str:
        messages = [
            {"role": "system", "content": self.system},
            {"role": "user",   "content": user_message},
        ]
        print(f"\nUser: {user_message}")
        while True:
            response = ollama.chat(
                model=self.model,
                messages=messages,
                tools=TOOL_DEFINITIONS,
            )
            message = response['message']
            messages.append(message)
            # No tool calls — model is done, return its reply
            if not message.get('tool_calls'):
                return message.get('content', '')
            # Execute each tool call and feed results back
            for tool_call in message['tool_calls']:
                func_name = tool_call['function']['name']
                args      = tool_call['function']['arguments']
                print(f"  -> Calling: {func_name}({args})")
                if func_name in TOOL_FUNCTIONS:
                    result = TOOL_FUNCTIONS[func_name](**args)
                else:
                    result = f"Error: tool '{func_name}' not found."
                print(f"  <- Result:  {result}")
                messages.append({
                    "role":    "tool",
                    "content": str(result),
                    "name":    func_name,
                })
# ─────────────────────────────────────────────
# DEMO
# ─────────────────────────────────────────────
if __name__ == "__main__":
    agent = BudgetAgent(model="llama3.1")

    queries = [
        "I spent Rs.1200 on lunch and coffee(food) today.",
        "Add Rs.850 for an Uber ride(transport) to the airport.",
        "Log Rs.3500 for a new pair of shoes (shopping).",
        "Log Rs.6800 on groceries(utilities) this week.",
        "How much have I spent on food so far?",
        "Give me a full summary of my spending this month.",
    ]
    for query in queries:
        answer = agent.run(query)
        print(f"\nAgent: {answer}")
        print("-" * 60)