"""
FuelWise

Free local AI agent for IIT Bhilai hostel mess decisions.

Run:
    # Terminal 1
    ollama serve

    # Terminal 2
    ollama pull llama3.2
    python3 mess_menu_agent.py

Optional smaller model:
    OLLAMA_MODEL=llama3.2:1b python3 mess_menu_agent.py
"""

import json
import os
import urllib.error
import urllib.request
from datetime import date, datetime
from difflib import get_close_matches
from pathlib import Path
from typing import Any, Optional


OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
RATING_LOG = Path(os.getenv("MEAL_RATING_LOG", "/tmp/mess_menu_ratings.jsonl"))


WEEKLY_MENU = {
    "Monday": {
        "breakfast": ["Poha", "Boiled Eggs", "Banana", "Tea"],
        "lunch": ["Dal Tadka", "Jeera Rice", "Roti", "Aloo Gobi", "Curd"],
        "snacks": ["Samosa", "Green Chutney", "Tea"],
        "dinner": ["Paneer Curry", "Roti", "Rice", "Cucumber Salad"],
    },
    "Tuesday": {
        "breakfast": ["Idli Sambar", "Coconut Chutney", "Banana", "Tea"],
        "lunch": ["Rajma", "Rice", "Roti", "Mixed Veg", "Curd"],
        "snacks": ["Veg Sandwich", "Tea"],
        "dinner": ["Egg Curry", "Roti", "Rice", "Onion Salad"],
    },
    "Wednesday": {
        "breakfast": ["Aloo Paratha", "Curd", "Pickle", "Tea"],
        "lunch": ["Chole", "Rice", "Roti", "Bhindi Fry", "Salad"],
        "snacks": ["Maggi", "Tea"],
        "dinner": ["Dal Fry", "Veg Pulao", "Roti", "Sprouts Salad"],
    },
    "Thursday": {
        "breakfast": ["Upma", "Boiled Eggs", "Banana", "Tea"],
        "lunch": ["Kadhi", "Rice", "Roti", "Beans Poriyal", "Curd"],
        "snacks": ["Pakora", "Tea"],
        "dinner": ["Chicken Curry", "Roti", "Rice", "Cucumber Salad"],
    },
    "Friday": {
        "breakfast": ["Dosa", "Sambar", "Coconut Chutney", "Tea"],
        "lunch": ["Dal Makhani", "Rice", "Roti", "Aloo Jeera", "Curd"],
        "snacks": ["Sprouts Chaat", "Tea"],
        "dinner": ["Paneer Bhurji", "Roti", "Rice", "Salad"],
    },
    "Saturday": {
        "breakfast": ["Bread Omelette", "Banana", "Tea"],
        "lunch": ["Veg Pulao", "Raita", "Roti", "Chana Masala"],
        "snacks": ["Pav Bhaji", "Tea"],
        "dinner": ["Dal Tadka", "Rice", "Roti", "Aloo Gobi", "Curd"],
    },
    "Sunday": {
        "breakfast": ["Poori Sabzi", "Tea"],
        "lunch": ["Chicken Biryani", "Veg Biryani", "Raita", "Salad"],
        "snacks": ["Cold Coffee", "Veg Sandwich"],
        "dinner": ["Khichdi", "Curd", "Papad", "Pickle"],
    },
}


def nutrition(calories: int, protein: int, carbs: int, fat: int, allergens: str, note: str) -> dict[str, Any]:
    return {
        "calories": calories,
        "protein": protein,
        "carbs": carbs,
        "fat": fat,
        "allergens": allergens.split() if allergens else [],
        "note": note,
    }


NUTRITION_DB = {
    "Poha": nutrition(260, 6, 42, 8, "peanut", "Light breakfast; add eggs or curd for protein."),
    "Boiled Eggs": nutrition(156, 13, 1, 11, "egg", "High-quality protein; useful for bulking or cutting."),
    "Banana": nutrition(105, 1, 27, 0, "", "Good quick carbs before class, gym, or sports."),
    "Tea": nutrition(70, 2, 10, 2, "milk", "Fine in moderation; sugar adds up quickly."),
    "Dal Tadka": nutrition(220, 12, 28, 7, "", "Reliable vegetarian protein base."),
    "Jeera Rice": nutrition(260, 5, 52, 4, "", "Easy carbs; portion size decides whether it fits a cut."),
    "Rice": nutrition(240, 4, 52, 1, "", "Simple carb source; pair with dal, egg, paneer, or chicken."),
    "Roti": nutrition(110, 3, 22, 2, "gluten", "Good controlled carb option."),
    "Aloo Gobi": nutrition(180, 4, 24, 8, "", "Decent vegetables, but not a protein source."),
    "Curd": nutrition(90, 5, 7, 4, "milk", "Good add-on for gut comfort and extra protein."),
    "Samosa": nutrition(280, 5, 34, 14, "gluten", "Tasty, but fried; limit during a cut."),
    "Green Chutney": nutrition(20, 1, 3, 1, "", "Mostly flavor; check spice tolerance."),
    "Paneer Curry": nutrition(320, 16, 12, 24, "milk", "Protein-rich but calorie dense."),
    "Cucumber Salad": nutrition(30, 1, 6, 0, "", "Great volume food; helps with fullness."),
    "Idli Sambar": nutrition(280, 10, 54, 3, "", "Light and balanced; sambar improves protein and fiber."),
    "Coconut Chutney": nutrition(110, 2, 5, 9, "coconut", "Calorie dense for a small serving."),
    "Rajma": nutrition(260, 14, 42, 4, "", "Strong vegetarian protein and fiber option."),
    "Mixed Veg": nutrition(140, 4, 18, 6, "", "Useful micronutrients; pair with protein."),
    "Veg Sandwich": nutrition(240, 8, 38, 6, "gluten", "Better snack than fried options."),
    "Egg Curry": nutrition(300, 18, 10, 20, "egg", "Great protein; watch gravy oil."),
    "Onion Salad": nutrition(35, 1, 8, 0, "", "Good crunch and volume."),
    "Aloo Paratha": nutrition(330, 8, 48, 12, "gluten", "Heavy breakfast; balance with curd and lighter lunch."),
    "Pickle": nutrition(25, 0, 2, 2, "", "High sodium; keep it small."),
    "Chole": nutrition(280, 13, 44, 6, "", "Good fiber and vegetarian protein."),
    "Bhindi Fry": nutrition(180, 4, 16, 11, "", "Vegetable option, often oil-heavy."),
    "Salad": nutrition(40, 1, 8, 0, "", "Easy way to improve fullness."),
    "Maggi": nutrition(360, 8, 52, 14, "gluten", "Comfort food; low satiety for the calories."),
    "Dal Fry": nutrition(240, 12, 30, 8, "", "Useful protein base, but oil can vary."),
    "Veg Pulao": nutrition(300, 7, 55, 7, "", "Good carb source; needs protein alongside."),
    "Sprouts Salad": nutrition(120, 9, 18, 2, "", "Excellent high-fiber snack or dinner add-on."),
    "Upma": nutrition(290, 7, 46, 9, "gluten", "Decent breakfast; add eggs for protein."),
    "Kadhi": nutrition(190, 8, 18, 9, "milk", "Comforting but not very high in protein."),
    "Beans Poriyal": nutrition(120, 4, 14, 5, "coconut", "Good vegetable side."),
    "Pakora": nutrition(310, 7, 32, 17, "", "Fried snack; best treated as occasional."),
    "Chicken Curry": nutrition(360, 28, 8, 24, "", "Best mess protein option when available."),
    "Dosa": nutrition(220, 6, 38, 5, "", "Light carb base; pair with sambar."),
    "Sambar": nutrition(140, 7, 22, 3, "", "Adds protein and fiber to South Indian breakfast."),
    "Dal Makhani": nutrition(330, 15, 34, 16, "milk", "Good protein, but richer than regular dal."),
    "Aloo Jeera": nutrition(210, 4, 30, 9, "", "Carb-heavy side."),
    "Sprouts Chaat": nutrition(160, 10, 24, 3, "", "One of the better mess snacks."),
    "Paneer Bhurji": nutrition(340, 18, 10, 25, "milk", "High protein, high fat; portion control matters."),
    "Bread Omelette": nutrition(360, 18, 38, 15, "egg gluten", "Solid breakfast for busy mornings."),
    "Raita": nutrition(110, 5, 10, 5, "milk", "Cooling side; adds some protein."),
    "Chana Masala": nutrition(300, 14, 46, 7, "", "Strong vegetarian protein and fiber."),
    "Pav Bhaji": nutrition(420, 10, 62, 15, "gluten milk", "Fun snack but calorie-heavy."),
    "Poori Sabzi": nutrition(450, 8, 58, 22, "gluten", "Weekend treat; avoid stacking with a heavy lunch."),
    "Chicken Biryani": nutrition(620, 30, 72, 24, "", "Good protein but calorie dense."),
    "Veg Biryani": nutrition(520, 12, 78, 18, "", "High-energy meal; add curd or sprouts if available."),
    "Cold Coffee": nutrition(240, 7, 34, 8, "milk", "Sugar-heavy drink; can replace, not accompany, a snack."),
    "Khichdi": nutrition(300, 11, 52, 6, "", "Easy dinner when digestion or workload is rough."),
    "Papad": nutrition(55, 2, 8, 2, "", "Crunchy side; can be salty."),
}


GOAL_GUIDES = {
    "bulk": (
        "Eat a calorie surplus with enough protein.",
        "Choose 1 protein anchor, 2 carb servings, vegetables, and curd if tolerated.",
        "Prefer eggs, paneer, chicken, dal, rajma, chole, curd, rice, and roti.",
        "Do not fill up only on fried snacks; they add calories without enough protein.",
    ),
    "cut": (
        "Eat high protein with controlled calories.",
        "Choose 1 protein anchor, 1 carb serving, and a large salad or vegetable side.",
        "Prefer eggs, dal, chicken, sprouts, curd, salad, and smaller rice/roti portions.",
        "Limit samosa, pakora, poori, Maggi, biryani, sweet drinks, and extra gravy.",
    ),
    "maintain": (
        "Keep energy steady without overthinking every meal.",
        "Choose 1 protein anchor, 1 to 2 carb servings, and vegetables.",
        "Build a balanced plate and adjust portions around gym, sports, and class load.",
        "Avoid turning every snack into a fried snack plus sugary tea combo.",
    ),
}


def outside_option(name: str, price: int, tags: str, reason: str) -> dict[str, Any]:
    return {"name": name, "price": price, "tags": set(tags.split()), "reason": reason}


OUTSIDE_OPTIONS = [
    outside_option("Egg bhurji with 2 rotis", 80, "protein spicy egg bulk cut", "High protein, filling, and usually available near campus."),
    outside_option("Chicken roll without mayo", 120, "protein chicken spicy bulk maintain", "Good protein when mess dinner is weak; skip mayo to control calories."),
    outside_option("Paneer roll with extra salad", 110, "protein paneer vegetarian bulk maintain", "Vegetarian protein option; extra salad improves fullness."),
    outside_option("Curd bowl with banana", 60, "sweet light vegetarian maintain cut", "Simple, cheap, and better than a sugary drink plus fried snack."),
    outside_option("Sprouts chaat", 50, "protein light vegetarian cut", "Best budget pick for protein, fiber, and fullness."),
    outside_option("Tandoori chicken half plate", 180, "protein chicken gym bulk cut", "Lean protein if you avoid creamy dips and extra butter."),
    outside_option("Masala dosa with sambar", 90, "south indian vegetarian maintain", "Comforting meal with a better balance than fried fast food."),
    outside_option("Milk plus peanut chikki", 45, "sweet budget bulk snack", "Cheap calories for bulking; avoid if peanut or milk allergy applies."),
]


ALL_DISHES = sorted(
    set(NUTRITION_DB) | {dish for daily_menu in WEEKLY_MENU.values() for dishes in daily_menu.values() for dish in dishes}
)


def normalise(text: str) -> str:
    return text.strip().lower().replace("_", " ").replace("-", " ")


def find_dish(dish: str) -> Optional[str]:
    wanted = normalise(dish)
    for known_dish in ALL_DISHES:
        if normalise(known_dish) == wanted:
            return known_dish
    matches = get_close_matches(dish, ALL_DISHES, n=1, cutoff=0.65)
    return matches[0] if matches else None


# ===== Tool Implementations =====

def get_today_menu(meal: str) -> str:
    day = date.today().strftime("%A")
    day_menu = WEEKLY_MENU[day]
    meal_key = normalise(meal)

    if meal_key in {"all", "full day", "today", "day"}:
        meals = day_menu.keys()
    elif meal_key in day_menu:
        meals = [meal_key]
    else:
        return f"Unknown meal '{meal}'. Try breakfast, lunch, snacks, dinner, or all."

    lines = [f"{day} mess menu:"]
    lines.extend(f"- {name.title()}: {', '.join(day_menu[name])}" for name in meals)
    return "\n".join(lines)


def get_nutrition(dish: str) -> str:
    matched = find_dish(dish)
    if not matched or matched not in NUTRITION_DB:
        suggestions = ", ".join(get_close_matches(dish, ALL_DISHES, n=3, cutoff=0.35))
        hint = f" Did you mean: {suggestions}?" if suggestions else ""
        return f"No nutrition data found for '{dish}'.{hint}"

    info = NUTRITION_DB[matched]
    allergens = ", ".join(info["allergens"]) if info["allergens"] else "none listed"
    return (
        f"{matched}: {info['calories']} kcal, {info['protein']}g protein, "
        f"{info['carbs']}g carbs, {info['fat']}g fat. "
        f"Allergens: {allergens}. Note: {info['note']}"
    )


def check_user_goals(goal: str) -> str:
    text = normalise(goal)
    if any(word in text for word in ["bulk", "gain", "muscle", "surplus"]):
        resolved = "bulk"
    elif any(word in text for word in ["cut", "fat loss", "lose", "deficit", "weight loss"]):
        resolved = "cut"
    elif any(word in text for word in ["maintain", "maintenance", "balanced", "normal"]):
        resolved = "maintain"
    else:
        return "Goal not recognized. Use one of: bulk, cut, maintain."

    summary, plate_rule, strategy, limit = GOAL_GUIDES[resolved]
    return f"Goal: {resolved}. {summary} Plate rule: {plate_rule} Mess strategy: {strategy} Limit: {limit}"


def suggest_outside_alternative(craving: str, budget: int) -> str:
    try:
        budget = int(budget)
    except (TypeError, ValueError):
        return "Budget must be a number in rupees."

    craving_words = set(normalise(craving).split())
    affordable = [item for item in OUTSIDE_OPTIONS if item["price"] <= budget]
    if not affordable:
        return f"No outside options under Rs {budget}. Fallback: banana, curd, or sprouts from the mess."

    def score(item: dict[str, Any]) -> tuple[int, int]:
        return (len(item["tags"] & craving_words), -item["price"])

    top = sorted(affordable, key=score, reverse=True)[:3]
    lines = [f"Best outside alternatives under Rs {budget} for '{craving}':"]
    lines.extend(f"- {item['name']} - Rs {item['price']}: {item['reason']}" for item in top)
    return "\n".join(lines)


def log_meal_rating(dish: str, rating: int) -> str:
    try:
        rating = int(rating)
    except (TypeError, ValueError):
        return "Rating must be a number from 1 to 5."
    if rating < 1 or rating > 5:
        return "Rating must be between 1 and 5."

    matched = find_dish(dish) or dish.strip().title()
    entry = {"timestamp": datetime.now().isoformat(timespec="seconds"), "dish": matched, "rating": rating}
    with RATING_LOG.open("a", encoding="utf-8") as file:
        file.write(json.dumps(entry) + "\n")
    return f"Logged {rating}/5 for {matched}. Thanks - the mess memory got sharper."


TOOL_FUNCTIONS = {
    "get_today_menu": get_today_menu,
    "get_nutrition": get_nutrition,
    "check_user_goals": check_user_goals,
    "suggest_outside_alternative": suggest_outside_alternative,
    "log_meal_rating": log_meal_rating,
}


# ===== Tool Definitions =====

def prop(prop_type: str, description: str, **extra: Any) -> dict[str, Any]:
    return {"type": prop_type, "description": description, **extra}


def tool(name: str, description: str, properties: dict[str, Any], required: list[str]) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": properties, "required": required},
        },
    }


TOOL_DEFINITIONS = [
    tool(
        "get_today_menu",
        "Get today's mess menu for breakfast, lunch, snacks, dinner, or all meals.",
        {"meal": prop("string", "Meal name: breakfast, lunch, snacks, dinner, or all.")},
        ["meal"],
    ),
    tool(
        "get_nutrition",
        "Get calories, macros, allergens, and a practical note for a dish.",
        {"dish": prop("string", "Dish name from the menu.")},
        ["dish"],
    ),
    tool(
        "check_user_goals",
        "Get meal-planning rules for bulk, cut, or maintain goals.",
        {"goal": prop("string", "Fitness goal, e.g. bulk, cut, maintain, gain muscle, or lose fat.")},
        ["goal"],
    ),
    tool(
        "suggest_outside_alternative",
        "Suggest outside food alternatives based on craving and budget.",
        {
            "craving": prop("string", "Craving, e.g. protein, spicy, sweet, chicken, vegetarian."),
            "budget": prop("integer", "Maximum budget in rupees."),
        },
        ["craving", "budget"],
    ),
    tool(
        "log_meal_rating",
        "Log a student's rating for a mess dish from 1 to 5.",
        {
            "dish": prop("string", "Dish being rated."),
            "rating": prop("integer", "Rating from 1 to 5.", minimum=1, maximum=5),
        },
        ["dish", "rating"],
    ),
]


class OllamaNotRunning(RuntimeError):
    pass


class OllamaModelMissing(RuntimeError):
    pass


class OllamaAPIError(RuntimeError):
    pass


# ===== ReAct Agent Loop =====

class MessMenuAgent:
    def __init__(self, model: str = OLLAMA_MODEL, host: str = OLLAMA_HOST) -> None:
        self.model = model
        self.host = host
        self.system_prompt = (
            "You are FuelWise, a practical food-planning agent for IIT Bhilai hostel students. "
            "Use tools before recommending dishes. Consider the user's goal, allergies, budget, and cravings. "
            "If no goal is provided, assume maintain. If allergies are mentioned, avoid matching allergens. "
            "Do not invent exact calories or protein values unless a tool provided them. "
            "Keep answers concise, friendly, and campus-realistic. Avoid medical claims."
        )

    def chat(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        payload = {"model": self.model, "messages": messages, "tools": TOOL_DEFINITIONS, "stream": False}
        request = urllib.request.Request(
            f"{self.host}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code == 404 or "not found" in body.lower():
                raise OllamaModelMissing from exc
            raise OllamaAPIError(f"Ollama API error {exc.code}: {body}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise OllamaNotRunning from exc

    def run(self, user_message: str) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message},
        ]

        for _ in range(6):
            message = self.chat(messages).get("message", {})
            messages.append(message)

            tool_calls = message.get("tool_calls") or []
            if not tool_calls:
                return message.get("content", "").strip() or "I could not generate a final recommendation."

            for call in tool_calls:
                result = self.run_tool(call.get("function", {}))
                messages.append(result)

        return "I used the tools several times but could not settle on a final answer."

    def run_tool(self, function_call: dict[str, Any]) -> dict[str, str]:
        name = function_call.get("name", "")
        arguments = parse_arguments(function_call.get("arguments", {}))
        print(f"  -> Calling: {name}({arguments})")

        try:
            result = TOOL_FUNCTIONS[name](**arguments)
        except KeyError:
            result = f"Unknown tool: {name}"
        except TypeError as exc:
            result = f"Tool input error for {name}: {exc}"
        except Exception as exc:
            result = f"Tool execution error for {name}: {exc}"

        print(f"  <- Result: {result}")
        return {"role": "tool", "tool_name": name, "content": str(result)}


def parse_arguments(arguments: Any) -> dict[str, Any]:
    if isinstance(arguments, dict):
        return arguments
    if isinstance(arguments, str):
        try:
            parsed = json.loads(arguments)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def offline_tool_preview() -> None:
    print("\nOffline tool preview:")
    print(get_today_menu("all"))
    print()
    print(check_user_goals("cut"))
    print()
    print(get_nutrition("Paneer Curry"))
    print()
    print(suggest_outside_alternative("protein vegetarian", 120))


def print_startup_help() -> None:
    print("FuelWise is ready.")
    print("Ask about today's menu, fitness goals, allergies, cravings, or ratings.")
    print("\nTry these example prompts:")
    print("- I am cutting. What should I eat for dinner today?")
    print("- I want high protein food under Rs 120. What should I order?")
    print("- I have a peanut allergy. Is today's breakfast safe?")
    print("- Log Paneer Curry as 4 out of 5.")
    print("Type 'exit', 'quit', or 'q' to stop.")


def handle_ollama_error(error: Exception, agent: MessMenuAgent) -> None:
    if isinstance(error, OllamaNotRunning):
        print("Ollama is not running. Start it with: ollama serve")
        print("Then run: ollama pull llama3.2")
        print("Then run: python3 mess_menu_agent.py")
    elif isinstance(error, OllamaModelMissing):
        print(f"Ollama is running, but '{agent.model}' is not downloaded.")
        print(f"Download it with: ollama pull {agent.model}")
    else:
        print(error)
    offline_tool_preview()


def main() -> None:
    agent = MessMenuAgent()
    print_startup_help()

    while True:
        query = input("\nYou: ").strip()
        if not query:
            continue
        if query.lower() in {"exit", "quit", "q"}:
            print("Bye. Eat smart, survive mess.")
            return

        try:
            print(f"\nAgent: {agent.run(query)}")
            print("-" * 60)
        except (OllamaNotRunning, OllamaModelMissing, OllamaAPIError) as exc:
            handle_ollama_error(exc, agent)
            return


if __name__ == "__main__":
    main()
