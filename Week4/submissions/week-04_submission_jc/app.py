from graph import chatbot
from langgraph.types  import Command
from langchain_core.messages import HumanMessage,AIMessage

CONFIG = {
    'configurable':{
        'thread_id':'thread_01'
        }
    }

while True:
    user_input = input('You :')

    if user_input.lower().strip() in ['exit','bye'] :
        print("good Bye!")
        break
    
    initial_state = {'messages':HumanMessage(content=user_input)}
    response = chatbot.invoke(initial_state,config=CONFIG)
    Bot = response['messages'][-1].content
    print(f"Bot: {Bot}")


    interrupts = response.get("__interrupt__", [])

    if interrupts:
        # Our interrupt payload is the string we passed to interrupt(...)
        prompt_to_human = interrupts[0].value
        print(f"HITL: {prompt_to_human}")
        decision = input("Your decision: ").strip().lower()

            # Resume graph with the human decision ("yes" / "no" / whatever)
        response = chatbot.invoke(Command(resume=decision),config=CONFIG) 

        Bot = response['messages'][-1].content
        print(f"Bot: {Bot}")
