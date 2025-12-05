# src/agents/payment_agent.py

import uuid
from src.models.state import State
from langgraph.types import interrupt
from src.utils.logger import logger

PAYMENT_GATEWAY = "https://www.razorpay.com/htequireoi78skj"


def payment_agent_node(state: State) -> State:
    logger.debug("[PAYMENT_AGENT] Start: %s", state)

    # Empty cart check
    if not state.cart:
        state.messages.append("Your cart is empty. Unable to proceed with payment.")
        state.payment_status = "failed"
        logger.warning("[PAYMENT_AGENT] Payment failed: Cart empty.")
        logger.debug("[PAYMENT_AGENT] End: %s", state)
        return state

    # Ask user to complete the payment
    logger.info("[PAYMENT_AGENT] Triggering payment_info interrupt for card details.")

    payment_status = interrupt({
        "target": "payment_info",
        "fields": [
            {
                "name": "payment_status",
                "prompt": f"💳 *Payment Required*\nPlease complete your payment by clicking the secure link below:\n{PAYMENT_GATEWAY}",
                "options": "",
            },
        ],
    })

    # Handle payment success or failure
    if payment_status.get("payment_status"):
        state.payment_status = "authorized"
        state.order_id = str(uuid.uuid4())[:8].upper()
        state.messages.append(f"✅ *Payment Successful!*")
        state.messages.append(f"🧾 *Order ID:* {state.order_id}")
        state.messages.append("Thank you for your purchase 🎉")
        logger.info("[PAYMENT_AGENT] Payment authorized. Order ID: %s", state.order_id)
    else:
        state.payment_status = "failed"
        state.messages.append("❌ Payment failed or was not completed.")
        state.messages.append("You can retry anytime by typing *checkout*.")
        logger.warning("[PAYMENT_AGENT] Payment failed or not completed.")

    logger.debug("[PAYMENT_AGENT] End: %s", state)
    return state
