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
    resume_data = {}
    for field in interrupt_value['fields']:
        if field['options']:
            print(field['options'])
        user_inp = input(field['prompt']+' :').strip()
        resume_data[field['name']] = user_inp
    result = app.invoke(Command(resume=resume_data), config=config)

result_state = State(**result)

print("\n=== 🛒 CART SUMMARY ===")
for i, item in enumerate(result_state.cart, 1):
    print(f"{i}. {item.identifier} - {item.price} {item.currency}")

print(f"\n💰 Total Amount: {result_state.cart_total:.2f}")
print(f"💳 Payment Status: {result_state.payment_status}\n")


# print(result['messages'][0])