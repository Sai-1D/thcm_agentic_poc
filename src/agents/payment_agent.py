# src/agents/payment_agent.py
import uuid
import random
from src.models.state import State

# Hardcoded valid credentials
VALID_CARD = "4111111111111111"
VALID_CVV = "123"


def payment_agent_node(state: State) -> State:
    if not state.cart:
        state.messages.append("Cart is empty. Cannot proceed to payment.")
        state.payment_status = "failed"
        return state

# Check card details
    if state.card_number == VALID_CARD and state.cvv == VALID_CVV:
        state.payment_status = "authorized"
        state.order_id = str(uuid.uuid4())[:8].upper()
        state.messages.append(f"Payment authorized. Order ID: {state.order_id}")
    else:
        state.payment_status = "failed"
        state.messages.append("Payment failed. Invalid card details.")

    return state
