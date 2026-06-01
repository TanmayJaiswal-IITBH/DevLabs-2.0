"""
Campus Life AI Agent
Domain: IIT Bhilai Student Assistant

Helps students with:
  - Mess menu and timings
  - Club and event information
  - Academic deadlines and exam schedules

Run:
    pip install ollama
    ollama pull llama3.2
    python agent.py
"""

import json
import ollama

# ─────────────────────────────────────────────
# TOOLS — functions the agent can call
# ─────────────────────────────────────────────

def get_mess_menu(day: str) -> str:
    """
    Get the mess menu for a given day of the week.

    Args:
        day: Day of the week, e.g. 'Monday', 'Tuesday', etc.
             Also accepts 'today' (mapped to Monday for demo).

    Returns:
        A formatted mess menu with breakfast, lunch, snacks, and dinner.
    """
    menu = {
        "monday": {
            "breakfast": "Poha, Boiled Eggs, Bread + Butter, Tea/Coffee",
            "lunch":     "Rajma, Steamed Rice, Chapati, Salad, Buttermilk",
            "snacks":    "Samosa + Chai",
            "dinner":    "Paneer Butter Masala, Dal Tadka, Rice, Chapati, Kheer",
        },
        "tuesday": {
            "breakfast": "Idli-Sambar, Coconut Chutney, Boiled Eggs, Tea/Coffee",
            "lunch":     "Chole, Jeera Rice, Chapati, Raita, Salad",
            "snacks":    "Bread Pakoda + Tea",
            "dinner":    "Mixed Veg, Yellow Dal, Rice, Chapati, Ice Cream",
        },
        "wednesday": {
            "breakfast": "Aloo Paratha, Curd, Pickle, Tea/Coffee",
            "lunch":     "Kadai Paneer, Dal Makhani, Rice, Chapati, Salad",
            "snacks":    "Maggi + Cold Drink",
            "dinner":    "Chicken Curry (non-veg block), Dal, Rice, Chapati, Halwa",
        },
        "thursday": {
            "breakfast": "Upma, Boiled Eggs, Bread + Jam, Tea/Coffee",
            "lunch":     "Aloo Matar, Moong Dal, Rice, Chapati, Pickle",
            "snacks":    "Vada Pav + Tea",
            "dinner":    "Shahi Paneer, Dal Fry, Rice, Chapati, Fruit Custard",
        },
        "friday": {
            "breakfast": "Puri-Sabzi, Boiled Eggs, Tea/Coffee",
            "lunch":     "Chana Masala, Jeera Rice, Chapati, Raita",
            "snacks":    "Pav Bhaji + Lassi",
            "dinner":    "Palak Paneer, Dal Tadka, Rice, Chapati, Gulab Jamun",
        },
        "saturday": {
            "breakfast": "Masala Dosa, Sambar, Chutney, Tea/Coffee",
            "lunch":     "Egg Curry (non-veg block), Jeera Rice, Chapati, Salad",
            "snacks":    "Bhel Puri + Tea",
            "dinner":    "Paneer Tikka Masala, Dal, Biryani, Raita, Kheer",
        },
        "sunday": {
            "breakfast": "Chole Bhature, Lassi — Special Sunday Brunch",
            "lunch":     "Special Thali: Dal Makhani, Paneer, Jeera Rice, Chapati, Sweet",
            "snacks":    "No snacks (late brunch)",
            "dinner":    "Chicken Biryani (non-veg block), Veg Pulao, Raita, Shahi Tukda",
        },
    }

    timings = {
        "breakfast": "7:30 AM – 9:30 AM",
        "lunch":     "12:30 PM – 2:30 PM",
        "snacks":    "5:00 PM – 6:00 PM",
        "dinner":    "7:30 PM – 9:30 PM",
    }

    key = day.lower().strip()
    if key == "today":
        key = "monday"  # Demo fallback

    if key not in menu:
        return (
            f"No menu found for '{day}'.\n"
            "Please enter a valid day: Monday through Sunday."
        )

    d = menu[key]
    lines = [f"📅 Mess Menu — {key.capitalize()}\n"]
    for meal, time in timings.items():
        lines.append(f"  🍽  {meal.capitalize()} ({time})")
        lines.append(f"     {d[meal]}")
    return "\n".join(lines)


def get_club_info(club_name: str) -> str:
    """
    Get information about a campus club or organization at IIT Bhilai.

    Args:
        club_name: Name or keyword of the club,
                   e.g. 'OpenLake', 'Aquatics', 'Music'.

    Returns:
        Club description, upcoming events, and contact details.
    """
    clubs = {
        "openlake": {
            "full_name":   "OpenLake — Open Source Community",
            "description": "IIT Bhilai's open-source developer community. Works on real-world projects like the CCPS Placement Portal, contributed to open-source tools, and runs DevLabs mentorship programs.",
            "upcoming":    [
                "DevLabs 2.0 — Week 1 submissions due this week",
                "Open Source Saturday — every Saturday 4 PM, CR Lab",
                "Hacktoberfest prep session — 2nd week of October",
            ],
            "contact": "openlake@iitbhilai.ac.in | Discord: discord.gg/openlake",
        },
        "aquatics": {
            "full_name":   "Aquatics Club — IIT Bhilai",
            "description": "Manages swimming and water sports activities on campus. Organizes Prayatna aquatics events, coordinates pool access, and trains competitive swimmers.",
            "upcoming":    [
                "Prayatna Inter-hostel Swimming Meet — TBD",
                "Beginner Swimming batch — registrations open",
                "Pool timings: 6–8 AM and 5–7 PM (weekdays)",
            ],
            "contact":    "aquatics.coordinator@iitbhilai.ac.in",
        },
        "music": {
            "full_name":   "Swarangini — Music Club",
            "description": "Campus music club covering classical, fusion, and western genres. Performs at Utkansh fest and inter-IIT cultural meets.",
            "upcoming":    [
                "Open mic night — Friday 8 PM, Amphitheatre",
                "Utkansh 2025 auditions — next month",
            ],
            "contact":    "music.club@iitbhilai.ac.in",
        },
        "coding": {
            "full_name":   "Algorithm & Coding Club (ACC)",
            "description": "Competitive programming club. Hosts Codeforces rounds, ICPC preparation sessions, and mock interviews.",
            "upcoming":    [
                "Weekly CP contest — Sunday 9 PM on Codeforces",
                "ICPC Team selection — September",
                "DP workshop — this Thursday 6 PM",
            ],
            "contact":    "acc@iitbhilai.ac.in",
        },
        "literary": {
            "full_name":   "Literati — Literary Club",
            "description": "Debate, creative writing, poetry, and quiz club. Runs the campus newsletter and represents IIT Bhilai at inter-IIT literary meets.",
            "upcoming":    [
                "Book club session: 'Midnight's Children' — Saturday 5 PM",
                "Debate: AI vs Human Creativity — next Wednesday",
            ],
            "contact":    "literati@iitbhilai.ac.in",
        },
    }

    key = club_name.lower().strip()
    for club_key, info in clubs.items():
        if club_key in key or key in club_key or any(w in key for w in club_key.split()):
            events = "\n".join(f"    • {e}" for e in info["upcoming"])
            return (
                f"🏛  {info['full_name']}\n\n"
                f"   {info['description']}\n\n"
                f"📌 Upcoming:\n{events}\n\n"
                f"📧 Contact: {info['contact']}"
            )

    available = ", ".join(clubs.keys())
    return (
        f"No club found matching '{club_name}'.\n"
        f"Known clubs: {available}"
    )


def get_academic_deadlines(course_or_event: str) -> str:
    """
    Look up upcoming academic deadlines, exam dates, or assignment
    due dates for IIT Bhilai courses.

    Args:
        course_or_event: Course name/code or event type,
                         e.g. 'CS201', 'endsem', 'assignments', 'quiz'.

    Returns:
        A list of relevant upcoming deadlines with dates.
    """
    deadlines = {
        "endsem": [
            ("CS201 — Computer Architecture",        "Nov 18, 2025  |  9:00 AM  |  LT-1"),
            ("CS251 — Systems Programming",           "Nov 20, 2025  |  9:00 AM  |  LT-2"),
            ("EC201 — VLSI Design",                  "Nov 22, 2025  |  2:00 PM  |  LT-1"),
            ("HS101 — Psychology & Disorders",       "Nov 24, 2025  |  9:00 AM  |  LT-3"),
            ("MA201 — Linear Algebra",               "Nov 26, 2025  |  9:00 AM  |  LT-1"),
            ("LAL101 — Introduction to Finance",     "Nov 28, 2025  |  2:00 PM  |  LT-2"),
        ],
        "quiz": [
            ("CS201 — Quiz 3",        "Oct 30, 2025  |  In-class"),
            ("CS251 — Quiz 2",        "Nov 01, 2025  |  In-class"),
            ("HS101 — Unit Test",     "Nov 05, 2025  |  LT-3"),
            ("MA201 — Mid-Quiz",      "Nov 03, 2025  |  In-class"),
        ],
        "assignments": [
            ("CS251 — RISC-V Paging Assignment",     "Oct 28, 2025  |  11:59 PM  |  Submit on Moodle"),
            ("CS201 — Cache Simulation Report",      "Oct 31, 2025  |  11:59 PM  |  Submit on Moodle"),
            ("HS101 — Case Study Write-up",          "Nov 02, 2025  |  11:59 PM  |  Submit on Moodle"),
            ("LAL101 — Portfolio Analysis",          "Nov 08, 2025  |  11:59 PM  |  Submit on Moodle"),
        ],
        "cs201": [
            ("CS201 — Quiz 3",     "Oct 30, 2025  |  In-class"),
            ("CS201 — Cache Lab",  "Oct 31, 2025  |  11:59 PM"),
            ("CS201 — End-Sem",    "Nov 18, 2025  |  9:00 AM  |  LT-1"),
        ],
        "cs251": [
            ("CS251 — Quiz 2",       "Nov 01, 2025  |  In-class"),
            ("CS251 — RISC-V Lab",   "Oct 28, 2025  |  11:59 PM"),
            ("CS251 — End-Sem",      "Nov 20, 2025  |  9:00 AM  |  LT-2"),
        ],
        "hs101": [
            ("HS101 — Unit Test",       "Nov 05, 2025  |  LT-3"),
            ("HS101 — Case Study",      "Nov 02, 2025  |  11:59 PM"),
            ("HS101 — End-Sem",         "Nov 24, 2025  |  9:00 AM  |  LT-3"),
        ],
    }

    key = course_or_event.lower().strip().replace(" ", "")
    matched_items = []

    for db_key, items in deadlines.items():
        if db_key in key or key in db_key:
            matched_items.extend(items)

    if matched_items:
        seen = set()
        unique_items = []
        for item in matched_items:
            if item not in seen:
                seen.add(item)
                unique_items.append(item)

        rows = "\n".join(f"  📌 {name}\n     {detail}" for name, detail in unique_items)
        return f"📅 Upcoming Deadlines ({course_or_event.title()}):\n\n{rows}"

    all_keys = ", ".join(deadlines.keys())
    return (
        f"No deadlines found for '{course_or_event}'.\n"
        f"Try one of: {all_keys}"
    )


# ─────────────────────────────────────────────
# TOOL REGISTRY
# ─────────────────────────────────────────────

TOOL_FUNCTIONS = {
    "get_mess_menu":          get_mess_menu,
    "get_club_info":          get_club_info,
    "get_academic_deadlines": get_academic_deadlines,
}

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_mess_menu",
            "description": (
                "Get the mess menu and meal timings for a given day of the week. "
                "Use when the student asks about food, meals, mess, or what's for lunch/dinner."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "day": {
                        "type": "string",
                        "description": "Day of the week, e.g. 'Monday', 'Friday', or 'today'.",
                    }
                },
                "required": ["day"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_club_info",
            "description": (
                "Get information about a campus club or student organization — "
                "description, upcoming events, and contact. "
                "Use when the student asks about clubs, societies, or campus groups."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "club_name": {
                        "type": "string",
                        "description": "Club name or keyword, e.g. 'OpenLake', 'Aquatics', 'Coding'.",
                    }
                },
                "required": ["club_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_academic_deadlines",
            "description": (
                "Look up upcoming academic deadlines, exam dates, and assignment due dates. "
                "Use when the student asks about exams, quizzes, assignments, or submission deadlines."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "course_or_event": {
                        "type": "string",
                        "description": "Course code or event type, e.g. 'CS201', 'endsem', 'assignments', 'quiz'.",
                    }
                },
                "required": ["course_or_event"],
            },
        },
    },
]


# ─────────────────────────────────────────────
# AGENT — ReAct loop
# ─────────────────────────────────────────────

class CampusAgent:
    """
    A conversational campus assistant for IIT Bhilai students.
    Uses a ReAct loop (Reason → Act → Observe) to answer queries
    about mess menu, clubs, and academic deadlines.
    """

    def __init__(self, model: str = "llama3.2"):
        self.model = model
        self.system = (
            "You are a friendly and helpful campus assistant for IIT Bhilai students. "
            "You help students with three things:\n"
            "  1. Mess menu and meal timings.\n"
            "  2. Campus club info and upcoming events.\n"
            "  3. Academic deadlines, exam dates, and assignment due dates.\n\n"
            "Always use the available tools to fetch accurate data. "
            "Never invent menu items, dates, or club details. "
            "Be concise, friendly, and use relevant emojis to make responses readable. "
            "If a query is outside your four domains, politely redirect the student."
        )

    def run(self, user_message: str) -> str:
        """Run the ReAct agent loop for a single user query."""
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

            assistant_msg = response.message
            messages.append(assistant_msg)

            if not assistant_msg.tool_calls:
                return assistant_msg.content or "[No response generated]"

            for tool_call in assistant_msg.tool_calls:
                fn_name = tool_call.function.name
                fn_args = tool_call.function.arguments

                if isinstance(fn_args, str):
                    try:
                        fn_args = json.loads(fn_args)
                    except json.JSONDecodeError:
                        fn_args = {}

                if fn_name not in TOOL_FUNCTIONS:
                    result = f"Error: Unknown tool '{fn_name}'."
                else:
                    print(f"  → Calling : {fn_name}({fn_args})")
                    result = TOOL_FUNCTIONS[fn_name](**fn_args)
                    print(f"  ← Result  :\n    "
                          + result.replace("\n", "\n    "))

                messages.append({
                    "role":    "tool",
                    "content": result,
                })


# ─────────────────────────────────────────────
# DEMO — 5 test queries
# ─────────────────────────────────────────────

if __name__ == "__main__":
    agent = CampusAgent(model="llama3.2")

    queries = [
        "What's for dinner tonight? Is there anything good?",
        "Tell me about OpenLake. Are there any upcoming events I should know about?",
        "When are my CS251 exams and assignments due?",
        "What are all the end-semester exams coming up?",
    ]

    for query in queries:
        answer = agent.run(query)
        print(f"\nAgent: {answer}")
        print("─" * 60)
