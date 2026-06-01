import os
import json
import sys
from typing import Any, cast
from groq import Groq

# Groq API key
GROQ_API_KEY = "YOUR_API_KEY"


def safe_print(*args: object, sep: str = " ", end: str = "\n") -> None:
    text = sep.join(str(item) for item in args)
    try:
        sys.stdout.write(text + end)
    except UnicodeEncodeError:
        fallback = (text + end).encode(sys.stdout.encoding or "utf-8", errors="replace")
        sys.stdout.buffer.write(fallback)

# ─────────────────────────────────────────────
# TOOLS — functions the agent can call
# ─────────────────────────────────────────────

def search_menu(category: str) -> str:
    """Browse menu items by category."""
    menu = {
        "starters": [
            "Paneer Tikka",
            "Chicken Seekh Kebab",
            "Veg Spring Rolls",
            "Crispy Corn",
            "Mutton Shammi Kebab",
        ],
        "mains": [
            "Butter Chicken",
            "Dal Makhani",
            "Paneer Butter Masala",
            "Chicken Biryani",
            "Veg Biryani",
            "Mutton Rogan Josh",
            "Palak Paneer",
        ],
        "breads": [
            "Butter Naan",
            "Garlic Naan",
            "Tandoori Roti",
            "Lachha Paratha",
        ],
        "desserts": [
            "Gulab Jamun",
            "Rasmalai",
            "Mango Kulfi",
            "Phirni",
        ],
        "drinks": [
            "Sweet Lassi",
            "Masala Chaas",
            "Fresh Lime Soda",
            "Mango Shake",
            "Masala Chai",
        ],
    }

    key = category.lower().strip()
    for cat, items in menu.items():
        if key in cat or cat in key:
            return (
                f"🍽️  {cat.upper()} ({len(items)} items):\n"
                + "\n".join(f"  • {item}" for item in items)
            )

    available = ", ".join(menu.keys())
    return (
        f"Category '{category}' not found.\n"
        f"Available categories: {available}"
    )


def get_item_details(item_name: str) -> str:
    """Get price, description, veg/non-veg tag, and spice level for a dish."""
    details = {
        # Starters
        "Paneer Tikka": {
            "price": 280,
            "description": "Soft cottage cheese cubes marinated in spiced yoghurt, grilled in tandoor.",
            "type": "Veg",
            "spice": "Medium",
        },
        "Chicken Seekh Kebab": {
            "price": 320,
            "description": "Minced chicken mixed with herbs and spices, skewered and grilled.",
            "type": "Non-Veg",
            "spice": "Medium",
        },
        "Veg Spring Rolls": {
            "price": 180,
            "description": "Crispy rolls stuffed with stir-fried veggies and noodles.",
            "type": "Veg",
            "spice": "Mild",
        },
        "Crispy Corn": {
            "price": 160,
            "description": "Golden fried sweet corn tossed with pepper, lime, and herbs.",
            "type": "Veg",
            "spice": "Mild",
        },
        "Mutton Shammi Kebab": {
            "price": 380,
            "description": "Tender mutton patties with chana dal, pan-fried to perfection.",
            "type": "Non-Veg",
            "spice": "High",
        },
        # Mains
        "Butter Chicken": {
            "price": 380,
            "description": "Tender chicken in a rich, creamy tomato-butter gravy.",
            "type": "Non-Veg",
            "spice": "Mild",
        },
        "Dal Makhani": {
            "price": 280,
            "description": "Slow-cooked black lentils simmered overnight in butter and cream.",
            "type": "Veg",
            "spice": "Mild",
        },
        "Paneer Butter Masala": {
            "price": 320,
            "description": "Paneer cubes in a velvety tomato-cashew gravy.",
            "type": "Veg",
            "spice": "Mild",
        },
        "Chicken Biryani": {
            "price": 420,
            "description": "Aromatic basmati rice layered with spiced chicken, slow-cooked dum style.",
            "type": "Non-Veg",
            "spice": "Medium",
        },
        "Veg Biryani": {
            "price": 320,
            "description": "Fragrant basmati rice with seasonal vegetables and whole spices.",
            "type": "Veg",
            "spice": "Medium",
        },
        "Mutton Rogan Josh": {
            "price": 480,
            "description": "Kashmiri-style slow-cooked mutton in bold aromatic spices.",
            "type": "Non-Veg",
            "spice": "High",
        },
        "Palak Paneer": {
            "price": 300,
            "description": "Paneer cubes in a smooth, spiced spinach gravy.",
            "type": "Veg",
            "spice": "Medium",
        },
        # Breads
        "Butter Naan": {
            "price": 60,
            "description": "Soft leavened bread baked in tandoor, brushed with butter.",
            "type": "Veg",
            "spice": "None",
        },
        "Garlic Naan": {
            "price": 80,
            "description": "Tandoor-baked naan topped with garlic and fresh coriander.",
            "type": "Veg",
            "spice": "None",
        },
        "Tandoori Roti": {
            "price": 40,
            "description": "Whole wheat flatbread baked in tandoor.",
            "type": "Veg",
            "spice": "None",
        },
        "Lachha Paratha": {
            "price": 70,
            "description": "Multi-layered flaky whole wheat paratha, crisped in butter.",
            "type": "Veg",
            "spice": "None",
        },
        # Desserts
        "Gulab Jamun": {
            "price": 120,
            "description": "Soft milk-solid dumplings soaked in rose-flavoured sugar syrup. Served warm.",
            "type": "Veg",
            "spice": "None",
        },
        "Rasmalai": {
            "price": 140,
            "description": "Spongy cottage cheese patties in chilled saffron-cardamom milk.",
            "type": "Veg",
            "spice": "None",
        },
        "Mango Kulfi": {
            "price": 130,
            "description": "Dense traditional ice cream infused with Alphonso mango.",
            "type": "Veg",
            "spice": "None",
        },
        "Phirni": {
            "price": 110,
            "description": "Chilled rice pudding set in earthen pots, topped with pistachios.",
            "type": "Veg",
            "spice": "None",
        },
        # Drinks
        "Sweet Lassi": {
            "price": 90,
            "description": "Thick chilled yoghurt drink blended with sugar and cardamom.",
            "type": "Veg",
            "spice": "None",
        },
        "Masala Chaas": {
            "price": 70,
            "description": "Spiced buttermilk with roasted cumin, ginger, and mint.",
            "type": "Veg",
            "spice": "Mild",
        },
        "Fresh Lime Soda": {
            "price": 80,
            "description": "Freshly squeezed lime with chilled soda — sweet, salted, or mixed.",
            "type": "Veg",
            "spice": "None",
        },
        "Mango Shake": {
            "price": 120,
            "description": "Thick creamy shake made with fresh Alphonso mangoes.",
            "type": "Veg",
            "spice": "None",
        },
        "Masala Chai": {
            "price": 50,
            "description": "Strong ginger-cardamom tea brewed with full-fat milk.",
            "type": "Veg",
            "spice": "Mild",
        },
    }

    # Flexible match (case-insensitive)
    item_lower = item_name.lower()
    for name, info in details.items():
        if name.lower() == item_lower or name.lower() in item_lower:
            tag = "🟢 Veg" if info["type"] == "Veg" else "🔴 Non-Veg"
            return (
                f"Item    : {name}\n"
                f"Price   : ₹{info['price']}\n"
                f"Type    : {tag}\n"
                f"Spice   : {info['spice']}\n"
                f"About   : {info['description']}"
            )

    return f"Item '{item_name}' not found. Use search_menu to browse available items."


def check_availability(item_name: str) -> str:
    """Check whether a menu item is available today."""
    availability = {
        "Paneer Tikka":           "Available",
        "Chicken Seekh Kebab":    "Available",
        "Veg Spring Rolls":       "Available",
        "Crispy Corn":            "Available",
        "Mutton Shammi Kebab":    "Sold Out",
        "Butter Chicken":         "Available",
        "Dal Makhani":            "Available",
        "Paneer Butter Masala":   "Available",
        "Chicken Biryani":        "Available",
        "Veg Biryani":            "Sold Out",
        "Mutton Rogan Josh":      "Available",
        "Palak Paneer":           "Available",
        "Butter Naan":            "Available",
        "Garlic Naan":            "Available",
        "Tandoori Roti":          "Available",
        "Lachha Paratha":         "Available",
        "Gulab Jamun":            "Available",
        "Rasmalai":               "Sold Out",
        "Mango Kulfi":            "Available",
        "Phirni":                 "Available",
        "Sweet Lassi":            "Available",
        "Masala Chaas":           "Available",
        "Fresh Lime Soda":        "Available",
        "Mango Shake":            "Available",
        "Masala Chai":            "Available",
    }

    item_lower = item_name.lower()
    for name, status in availability.items():
        if name.lower() == item_lower or name.lower() in item_lower:
            if status == "Available":
                return f"✅ {name} is available and ready to order!"
            else:
                return f"❌ Sorry, {name} is SOLD OUT today."

    return f"Item '{item_name}' not found in today's menu."


def place_order(items: list) -> str:
    """
    Place an order for a list of item names.
    Returns an itemised bill with subtotal, taxes, and grand total.
    """
    prices = {
        "Paneer Tikka": 280, "Chicken Seekh Kebab": 320, "Veg Spring Rolls": 180,
        "Crispy Corn": 160, "Mutton Shammi Kebab": 380, "Butter Chicken": 380,
        "Dal Makhani": 280, "Paneer Butter Masala": 320, "Chicken Biryani": 420,
        "Veg Biryani": 320, "Mutton Rogan Josh": 480, "Palak Paneer": 300,
        "Butter Naan": 60, "Garlic Naan": 80, "Tandoori Roti": 40,
        "Lachha Paratha": 70, "Gulab Jamun": 120, "Rasmalai": 140,
        "Mango Kulfi": 130, "Phirni": 110, "Sweet Lassi": 90,
        "Masala Chaas": 70, "Fresh Lime Soda": 80, "Mango Shake": 120,
        "Masala Chai": 50,
    }

    sold_out = {"Mutton Shammi Kebab", "Veg Biryani", "Rasmalai"}

    if not items:
        return "No items provided. Please specify what you'd like to order."

    bill_lines = ["=" * 38, "       TADKA HOUSE", "       Order Summary", "=" * 38]
    subtotal = 0
    rejected = []

    for item in items:
        # Flexible name match
        matched_name = None
        item_lower = item.lower()
        for name in prices:
            if name.lower() == item_lower or name.lower() in item_lower:
                matched_name = name
                break

        if not matched_name:
            rejected.append(f"'{item}' — not found on menu")
            continue

        if matched_name in sold_out:
            rejected.append(f"'{matched_name}' — sold out today")
            continue

        price = prices[matched_name]
        subtotal += price
        bill_lines.append(f"  {matched_name:<24} ₹{price:>5,}")

    if rejected:
        bill_lines.append("\n  Could not add:")
        for r in rejected:
            bill_lines.append(f"    ✗ {r}")

    if subtotal == 0:
        return "None of the requested items could be added to the order."

    gst = int(subtotal * 0.05)          # 5% GST on food
    service_charge = int(subtotal * 0.10)  # 10% service charge
    grand_total = subtotal + gst + service_charge

    bill_lines += [
        "-" * 38,
        f"  {'Subtotal':<24} ₹{subtotal:>5,}",
        f"  {'GST (5%)':<24} ₹{gst:>5,}",
        f"  {'Service Charge (10%)':<24} ₹{service_charge:>5,}",
        "=" * 38,
        f"  {'GRAND TOTAL':<24} ₹{grand_total:>5,}",
        "=" * 38,
        "\n  Thank you for dining at Tadka House! 🙏",
        "  Your order has been placed successfully.",
    ]

    return "\n".join(bill_lines)


# ─────────────────────────────────────────────
# TOOL REGISTRY
# ─────────────────────────────────────────────

TOOL_FUNCTIONS = {
    "search_menu":       search_menu,
    "get_item_details":  get_item_details,
    "check_availability": check_availability,
    "place_order":       place_order,
}

# Adjusted to standard OpenAI/Groq tool schema format
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_menu",
            "description": (
                "Browse the restaurant menu by category. "
                "Categories: starters, mains, breads, desserts, drinks."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Menu category, e.g. 'starters', 'mains', 'drinks'.",
                    }
                },
                "required": ["category"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_item_details",
            "description": (
                "Get detailed information about a specific menu item: "
                "price, description, veg/non-veg tag, and spice level."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "item_name": {
                        "type": "string",
                        "description": "Exact or approximate name of the dish, e.g. 'Butter Chicken'.",
                    }
                },
                "required": ["item_name"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check whether a specific menu item is available or sold out today.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_name": {
                        "type": "string",
                        "description": "Name of the dish to check.",
                    }
                },
                "required": ["item_name"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "place_order",
            "description": (
                "Place a food order for one or more items. "
                "Returns an itemised bill with GST and service charge. "
                "Always check availability before placing an order."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of dish names to order, e.g. ['Butter Chicken', 'Garlic Naan'].",
                    }
                },
                "required": ["items"],
            },
        }
    },
]


# ─────────────────────────────────────────────
# AGENT — ReAct loop
# ─────────────────────────────────────────────

class RestaurantAgent:
    def __init__(self):
        # Groq client initialization
        self.client = Groq(api_key=GROQ_API_KEY)
        self.system_prompt = (
            "You are a warm and helpful food ordering assistant at Tadka House, "
            "a casual Indian multi-cuisine restaurant. "
            "Help customers browse the menu, learn about dishes, "
            "and place their order. "
            "Always check a dish's availability before recommending it or placing an order. "
            "When a customer wants to order, collect all items first, then call place_order once. "
            "Be friendly, concise, and make the dining experience delightful."
        )

    def run(self, user_message: str) -> str:
        # Start message history with System instructions and User message
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]

        while True:
            # Send context to Groq to get the next step
            response = self.client.chat.completions.create(
                model="openai/gpt-oss-20b", # Tool-capable Groq model
                messages=cast(Any, messages),
                tools=cast(Any, TOOL_DEFINITIONS),
                tool_choice="auto",
                max_tokens=1024,
            )

            response_message = response.choices[0].message

            # Append the assistant's message as a serializable dict so the history can be reused
            messages.append({
                "role": getattr(response_message, "role", "assistant"),
                "content": getattr(response_message, "content", "") or "",
            })

            # If there are no tool calls, the model has finished its reasoning and is replying to the user
            if not response_message.tool_calls:
                return response_message.content or ""

            # Action + Observation — execute tool calls and feed results back
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                
                # Safely parse arguments
                function_args = tool_call.function.arguments
                if isinstance(function_args, str):
                    try:
                        function_args = json.loads(function_args)
                    except json.JSONDecodeError:
                        function_args = {}
                elif function_args is None:
                    function_args = {}

                # Execute mapped function
                if function_name in TOOL_FUNCTIONS:
                    result = TOOL_FUNCTIONS[function_name](**function_args)
                else:
                    result = f"Error: Tool '{function_name}' not found."
                
                # Append the tool result back into the message history
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": str(result),
                })


# ─────────────────────────────────────────────
# DEMO
# ─────────────────────────────────────────────

if __name__ == "__main__":
    agent = RestaurantAgent()
    safe_print("Welcome to the Tadka House ordering assistant!")
    safe_print("Type 'menu', 'details <item>', 'availability <item>', or 'order <item1>, <item2>, ...'.")
    safe_print("Type 'quit' or 'exit' to end the session.")

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit", "q"}:
            safe_print("Goodbye! Thank you for visiting Tadka House.")
            break

        answer = agent.run(user_input)
        safe_print(f"\nAgent: {answer}")
        safe_print("-" * 60)