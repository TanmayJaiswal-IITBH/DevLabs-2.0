from langgraph.graph import StateGraph,START,END
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage,HumanMessage,AIMessage
from typing import Annotated,TypedDict
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_core.tools import tool
from langgraph.types import interrupt
from langchain_community.tools import DuckDuckGoSearchRun
from memory import checkpointer

import os 
load_dotenv()                 ## create your .env file and store the api key in it 
api_keey=os.getenv("GROQ_API_KEY")
llm = ChatGroq(model="llama-3.3-70b-versatile",api_key=api_keey)

from langgraph.graph.message import add_messages
class ChatState(TypedDict):
    messages :  Annotated[list[BaseMessage],add_messages]

search_tool = DuckDuckGoSearchRun(region="us-en")

import requests
@tool
def wikipedia_search(topic: str):
    """
    Fetch the information about that topic mentioned in the Wikipedia by using the url.
    """
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
    headers = {'User-Agent':'ResearchAssistant/1.0 (https://github.com/jayakanala)'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()

        return data.get("extract")

    except requests.exceptions.HTTPError:
        return f"Wikipedia page '{topic}' not found."

    except requests.exceptions.RequestException as e:
        return str(e)

@tool
def summarization_topic(text:str):
    """
    Summarize the given research into:
    - What is it?
    - Why is it important?
    - How does it work?
    - Consequences or applications
    - Future scope
    """
    prompt = f"""
    Summarize the following information.

    Information:
    {text}

    Format:
    1. What is it?
    2. Why is it important?
    3. How does it work?
    4. Consequences/Applications
    5. Future scope
    """
    response = llm.invoke(prompt)
    
    return response.content


@tool
def reveal_summary(summary:str) :
    """
    Ask the user for approval before revealing the generated summary.
    """
    decision = interrupt(
        "The summary is ready. Do you want to see it? (yes/no)"
    )

    if decision.lower() == "yes":
        return summary

    return "Summary was cancelled."


# ## ### end tools ### ## #

tools = [wikipedia_search,search_tool,summarization_topic,reveal_summary]
llm_with_tools = llm.bind_tools(tools)

def chat_node(state:ChatState):
    messages = state['messages']
    response = llm_with_tools.invoke(messages)
    return {'messages':[response]}

tool_node = ToolNode(tools)

graph = StateGraph(ChatState)
graph.add_node('chat_node',chat_node)
graph.add_node('tools',tool_node)
graph.add_edge(START,'chat_node')
graph.add_conditional_edges('chat_node',tools_condition)
graph.add_edge('tools','chat_node')

chatbot = graph.compile(checkpointer=checkpointer)



