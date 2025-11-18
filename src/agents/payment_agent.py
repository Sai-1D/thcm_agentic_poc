# src/agents/payment_agent.py

import uuid
from src.models.state import State
from langgraph.types import interrupt
from src.utils.logger import logger

# Hardcoded valid credentials
VALID_CARD = "1234567890"
VALID_CVV = "123"

def payment_agent_node(state: State) -> State:
    logger.debug("[PAYMENT_AGENT] Start: %s", state)

    if not state.cart:
        state.messages.append("Cart is empty. Cannot proceed to payment.")
        state.payment_status = "failed"
        logger.warning("[PAYMENT_AGENT] Payment failed: Cart is empty.")
        logger.info("[PAYMENT_AGENT] End: %s", state)
        return state

    # Trigger interrupt for card details
    logger.info("[PAYMENT_AGENT] Triggering payment_info interrupt for card details.")

    card_details = interrupt({
        "target": "payment_info",
        "fields": [
            {"name": "card_number", "prompt": "Please enter your card number:", "options": ""},
            {"name": "cvv", "prompt": "Please enter your CVV:", "options": ""},
        ],
    })

    logger.info("[PAYMENT_AGENT] Received card details: %s", card_details)
    state.card_number, state.cvv = card_details['card_number'], card_details['cvv']

    if state.card_number == VALID_CARD and state.cvv == VALID_CVV:
        state.payment_status = "authorized"
        state.order_id = str(uuid.uuid4())[:8].upper()
        state.messages.append(f"Your payment was successful! Order ID: {state.order_id}")
        state.messages.append("Thank you for your purchase 🎉")
        logger.info("[PAYMENT_AGENT] Payment authorized. Order ID: %s", state.order_id)
    else:
        state.payment_status = "failed"
        state.messages.append("Payment failed. Invalid card details.")
        logger.warning("[PAYMENT_AGENT] Payment failed: Invalid card details.")

    logger.debug("[PAYMENT_AGENT] End: %s", state)
    return state
