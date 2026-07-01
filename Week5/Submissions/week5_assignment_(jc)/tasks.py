from crewai import Task
from agents import researcher,writer,reviewer

research_task = Task(
    description=(
        "Research the topic '{topic}'. "
        "Collect the most important facts, key concepts, applications, "
        "advantages, and challenges."
    ),
    expected_output=(
        "A detailed research report containing accurate facts and key points."
    ),
    agent=researcher
)

writing_task = Task(
    description=(
        "using the researcher findings,write a well-structured article"
        "with an introduction , main content and conclusion"
    ),
    expected_output=(
         "A clear, informative, and well-organized article."
    ),
    agent=writer
)

review_task = Task(
    description=(
        "Review the article for grammar, clarity, readability, "
        "and completeness and Improve it wherever it is necessary."
    ),
    expected_output=(
        "A polished , error free , easily understandable article"
    ),
    agent=reviewer
)
