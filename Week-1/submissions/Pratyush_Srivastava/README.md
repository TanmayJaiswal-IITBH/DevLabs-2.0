# Budget Tracker Agent

### Description
A ReAct-based AI agent that helps users track their monthly expenses, monitor spending by category, check budget utilization, and generate spending summaries. The agent uses tool calling with a local LLM (Llama 3.1 via Ollama) to perform accurate budget calculations and expense management.

---

## Tools Used

### 1. `log_expense`
Logs a new expense with:
- Amount
- Category
- Description

### 2. `get_category_total`
Returns:
- Total amount spent in a category
- Budget utilization percentage
- Remaining budget

### 3. `check_budget_limit`
Checks whether a category is:
- Within budget
- Nearing the budget limit
- Over budget

### 4. `get_spending_summary`
Generates a complete month-to-date spending summary across all categories.

---

## Budget Categories

- Food
- Transport
- Entertainment
- Shopping
- Health
- Utilities
- Other

---

## Sample Queries & Outputs

### Query 1

**User:**
```text
I spent Rs.1200 on lunch and coffee(food) today.
```

**Agent:**
```text
Logged Rs.1,200 under 'food' — lunch and coffee. (Entry #1)
```

---

### Query 2

**User:**
```text
Add Rs.850 for an Uber ride(transport) to the airport.
```

**Agent:**
```text
Logged Rs.850 under 'transport' — Uber ride to the airport. (Entry #2)
```

---

### Query 3

**User:**
```text
How much have I spent on food so far?
```

**Agent:**
```text
[FOOD] Spent Rs.1,200 of Rs.8,000 limit (15% used) — on track. Rs.6,800 remaining.
```

---

### Query 4

**User:**
```text
Give me a full summary of my spending this month.
```

**Agent:**
```text
Monthly Spending Summary

food             15%  Rs.1,200 / Rs.8,000
transport        28%  Rs.850 / Rs.3,000
shopping         58%  Rs.3,500 / Rs.6,000
utilities       136%  Rs.6,800 / Rs.5,000 [OVER]

Total spent: Rs.12,350 of Rs.31,000 (39%)
```
