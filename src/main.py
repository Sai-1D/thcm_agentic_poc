# src/main.py
from src.models.state import State
from langgraph.types import Command
from src.graph import app

state = State()
user_input = input("\n\nUser: ")
state.user_query = user_input.strip()

config = {"configurable": {"thread_id": "session-001"}}
result = app.invoke(state, config=config)
while "__interrupt__" in result:
    interrupt_value = result["__interrupt__"][0].value
    interrupt_type = interrupt_value["type"]

    if interrupt_type == "product_selection":
        print(interrupt_value["question"])
        print(interrupt_value["options"])
        user_choice = input("Enter article number: ").strip()
        result = app.invoke(Command(resume={"article_number": user_choice}), config=config)

    elif interrupt_type == "payment_info":
        print(interrupt_value["question"])
        card_number = input("Enter card number: ").strip()
        cvv = input("Enter CVV: ").strip()
        result = app.invoke(Command(resume={"card_number": card_number, "cvv": cvv}), config=config)
    else:
        print("Unknown Interrupt")
        break

print(State(**result))