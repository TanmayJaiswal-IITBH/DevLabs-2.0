import requests
from pydantic import BaseModel , field_validator
import anthropic
from typing import Any
import os

class NumericInput(BaseModel):
    a : int
    b : int 
    @field_validator("a","b")
    @classmethod
    def must_be_positive(cls,v) -> int:
        if v <= 0 :
            raise ValueError("values should be positive")
        return v
        
class WeatherInput(BaseModel):
    city : str
    @field_validator("city")
    @classmethod
    def must_not_empty(cls,v) -> str:
        if not v.strip():
            raise ValueError("city sholud not empty")
        return v.strip()

def addition(a:int,b:int):
    return a+b

def multiplier(a:int,b:int):
    return a*b

def get_weather(city:str):

    try:
        city = city.title().strip()
        response = requests.get(url=f"https://wttr.in/{city}?format=3",timeout=5,)

        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e :
        return f"Couldn't fetch the {city} details as {e}"
 

class Tool:

    def __init__(
        self,
        name: str,
        description: str,
        input_model: type[BaseModel],
        func):

        self.name = name
        self.description = description
        self.input_model = input_model
        self.func = func

    def run(self, raw_input: dict[str, Any]) -> Any:
        try:
            validated = self.input_model(**raw_input)
            return self.func(**validated.model_dump())
        except Exception as e :
            return f"Tool {self.name} failed as {e}"
        
    def to_claude_definition(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_model.model_json_schema(),}
    
ToolS = [
     Tool(
        name="get_weather",
        description=(
            "Get the current weather for a city. "
            "Always use this tool when the user asks about weather — do not guess."
        ),
        input_model=WeatherInput,
        func=get_weather,) ,
    Tool(
        name = "addition",
        description=("add the two numbers available in the given prompt"),
        input_model=NumericInput,
        func=addition,),
    Tool(
        name="multiplier",
        description=("multiply the two numbers available in the given prompt"),
        input_model=NumericInput,
        func=multiplier,) , ]

TOOL_MAP: dict[str, Tool] = {t.name: t for t in ToolS}

class Agent():
    def __init__(self):
        self.client = anthropic.Anthropic(api_key = "your_api_key")
        self.tool_definitions = [t.to_claude_definition() for t in ToolS]

    def run(self,user_msg:str)->str:
        messages:list[dict[str,Any]] = [{"role":"user" , "content" : user_msg}]
        while True:
            response = self.client.messages.create(
                model="claude-opus-4-7",
                max_tokens=1024,
                system=(
                    "You are a helpful research assistant. "
                    "Use tools to find real information. "
                    "Never guess — if you need data, call the relevant tool."
                ),
                tools=self.tool_definitions,
                messages=messages,)
            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                for section in response.content:
                    if section.type == "text":
                        return section.text
            
            tool_results = []
            for section in response.content:
                if section.type == "tool_use":
                    result = TOOL_MAP[section.name].run(section.input)
                    print(f"{result}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": section.id,
                        "content": result,
                    })
            messages.append({"role": "user", "content": tool_results})
        
agent = Agent()

query = input(str("ask about addition,multiplication , weatehr of a city :\n"))

print(agent.run(query))
