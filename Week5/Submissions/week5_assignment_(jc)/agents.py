from crewai import Agent,LLM
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os 

load_dotenv()       ## create your .env file and store the api key in it 

# api_keey=os.getenv("GROQ_API_KEY")                                      ##NOt worked bcoz verison compatibility
# llm = ChatGroq(model="llama-3.3-70b-versatile",api_key=api_keey)        ##crewai=1.15.1 and langchain-groq=1.1.3

llm = LLM(
    model="groq/llama-3.3-70b-versatile"
    )

researcher = Agent(
    role="Research Researcher",
    goal="Collect accurate and relevant information about the given topic.",
    backstory=(
        "You are an experienced researcher who gathers factual information "
        "from reliable sources and identifies the key points of a topic."
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm
)

writer = Agent(
    role="Writer",
    goal="Transform the research findings into a clear, well-structured, and engaging article.",
    backstory=(
        "You are a skilled technical writer with expertise in organizing "
        "complex information into simple, coherent, and reader-friendly content. "
        "Your writing is accurate, logical, and easy to understand."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False
)

reviewer = Agent(
    role="Reviewer",
    goal="Review the article for accuracy, clarity, grammar, and completeness before producing the final version.",
    backstory=(
        "You are an experienced editor who specializes in proofreading and "
        "improving written content. You ensure the article is grammatically "
        "correct, well-organized, concise, and easy to read while preserving "
        "the original meaning."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False
)