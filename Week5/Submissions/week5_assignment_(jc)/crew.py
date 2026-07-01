from crewai import Crew,Process
from agents import researcher,writer,reviewer
from tasks import research_task,writing_task,review_task

Agents = [researcher,writer,reviewer]

Tasks = [research_task,writing_task,review_task]

CREW = Crew(
    agents=Agents,
    tasks=Tasks,
    process=Process.sequential,
    verbose=True
)