import os
import requests
from urllib.parse import quote
from typing import Callable, Any

from pydantic import (
    BaseModel,
    ValidationError,
    field_validator,
)

from langchain_groq import ChatGroq
from langchain_core.messages import (
    HumanMessage,
    ToolMessage,
)

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

MAX_STEPS = 10

if not os.getenv("GROQ_API_KEY"):
    raise RuntimeError(
        "GROQ_API_KEY environment variable is not set."
    )

# --------------------------------------------------
# INPUT SCHEMAS
# --------------------------------------------------

class WeatherInput(BaseModel):
    city: str

    @field_validator("city")
    @classmethod
    def validate_city(cls, v: str):
        v = v.strip()
        if not v:
            raise ValueError("City cannot be empty")
        return v


class SearchInput(BaseModel):
    query: str
    max_results: int = 5

    @field_validator("max_results")
    @classmethod
    def validate_results(cls, v: int):
        return max(1, min(v, 10))


class CurrencyInput(BaseModel):
    from_currency: str
    to_currency: str
    amount: float = 1.0

    @field_validator(
        "from_currency",
        "to_currency",
    )
    @classmethod
    def normalize_currency(cls, v: str):
        return v.strip().upper()


# --------------------------------------------------
# TOOLS
# --------------------------------------------------

def get_weather(city: str) -> str:
    try:
        city = quote(city)

        response = requests.get(
            f"https://wttr.in/{city}?format=3",
            timeout=5,
        )

        response.raise_for_status()

        return response.text.strip()

    except requests.RequestException as e:
        return f"Weather lookup failed: {str(e)}"


def search_web(
    query: str,
    max_results: int = 5
) -> str:
    try:
        response = requests.get(
            "https://api.duckduckgo.com/",
            params={
                "q": query,
                "format": "json",
                "no_html": 1,
            },
            timeout=5,
        )

        response.raise_for_status()

        data = response.json()

        results = []

        for item in data.get("RelatedTopics", []):
            if isinstance(item, dict) and "Text" in item:
                results.append(item["Text"])

        results = results[:max_results]

        if results:
            return "\n".join(
                f"• {r}" for r in results
            )

        abstract = data.get("AbstractText")

        if abstract:
            return abstract

        return "No results found."

    except requests.RequestException as e:
        return f"Search failed: {str(e)}"


def convert_currency(
    from_currency: str,
    to_currency: str,
    amount: float = 1.0,
) -> str:

    try:
        response = requests.get(
            f"https://open.er-api.com/v6/latest/{from_currency}",
            timeout=5,
        )

        response.raise_for_status()

        data = response.json()

        if data.get("result") != "success":
            return "Currency API returned an error."

        rate = data["rates"].get(to_currency)

        if rate is None:
            return f"Unsupported currency: {to_currency}"

        converted = round(amount * rate, 2)

        return (
            f"{amount} {from_currency} = "
            f"{converted} {to_currency}"
        )

    except requests.RequestException as e:
        return f"Currency conversion failed: {str(e)}"


# --------------------------------------------------
# TOOL WRAPPER
# --------------------------------------------------

class Tool:

    def __init__(
        self,
        name: str,
        description: str,
        input_model: type[BaseModel],
        func: Callable[..., str],
    ):
        self.name = name
        self.description = description
        self.input_model = input_model
        self.func = func

    def run(
        self,
        raw_input: dict[str, Any]
    ) -> str:

        try:
            validated = self.input_model(
                **raw_input
            )

            return self.func(
                **validated.model_dump()
            )

        except ValidationError as e:
            return (
                "Validation Error:\n"
                f"{str(e)}"
            )

        except Exception as e:
            return (
                f"Tool Execution Error: {e}"
            )

    def to_groq_tool(self):

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters":
                    self.input_model.model_json_schema(),
            },
        }


# --------------------------------------------------
# TOOL REGISTRY
# --------------------------------------------------

TOOLS = [
    Tool(
        "get_weather",
        "Get current weather for a city.",
        WeatherInput,
        get_weather,
    ),
    Tool(
        "search_web",
        (
            "Search the web for information. "
            "Use for recent events and facts."
        ),
        SearchInput,
        search_web,
    ),
    Tool(
        "convert_currency",
        (
            "Convert currency using live exchange rates. "
            "For multiple target currencies, call "
            "the tool once per currency."
        ),
        CurrencyInput,
        convert_currency,
    ),
]

TOOL_MAP = {
    tool.name: tool
    for tool in TOOLS
}

# --------------------------------------------------
# MODEL
# --------------------------------------------------

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
)

llm_with_tools = llm.bind_tools(
    [tool.to_groq_tool() for tool in TOOLS]
)

# --------------------------------------------------
# AGENT
# --------------------------------------------------

class ResearchAgent:

    def run(
        self,
        user_message: str
    ) -> str:

        messages = [
            HumanMessage(
                content=user_message
            )
        ]

        for step in range(MAX_STEPS):

            response = llm_with_tools.invoke(
                messages
            )

            messages.append(response)

            if not response.tool_calls:
                return str(response.content)

            for tool_call in response.tool_calls:

                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                print(
                    f"\n[Tool] "
                    f"{tool_name}"
                )
                print(
                    f"[Args] "
                    f"{tool_args}"
                )

                tool = TOOL_MAP.get(tool_name)

                if not tool:
                    result = (
                        f"Unknown tool: "
                        f"{tool_name}"
                    )
                else:
                    result = tool.run(
                        tool_args
                    )

                print(
                    f"[Result] "
                    f"{result}"
                )

                messages.append(
                    ToolMessage(
                        content=result,
                        tool_call_id=tool_call["id"],
                    )
                )

        return (
            "Stopped after reaching "
            f"{MAX_STEPS} tool iterations."
        )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    agent = ResearchAgent()

    while True:

        query = input(
            "\nYou: "
        ).strip()

        if query.lower() in {
            "exit",
            "quit",
        }:
            break

        answer = agent.run(query)

        print(
            f"\nAgent: "
            f"{answer}"
        )
