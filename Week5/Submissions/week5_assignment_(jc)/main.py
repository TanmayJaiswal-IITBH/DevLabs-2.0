from crew import CREW

topic = str(input("Type the topic name:"))

result = CREW.kickoff(
    inputs = {
        "topic" : topic
    }
)

print(result)
## to create virtual environment python python -m venv crew_env