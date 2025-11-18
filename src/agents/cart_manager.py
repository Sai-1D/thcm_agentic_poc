# src/agents/cart_manager.py

from src.models.state import State
from langgraph.types import interrupt
from src.utils.logger import logger

def cart_manager_node(state: State) -> State:
    logger.debug("[CART] Enter Cart Manager node, current state: %s", state)

    if not state.selected_products:
        logger.info("[CART] No product selected to add to cart.")
        state.messages.append("No product selected to add to cart.")
        return state

    for product in state.selected_products:
        state.cart.append(product)
        if product.price:
            state.cart_total += product.price
        logger.info("[CART] Added to cart: %s (%s %s)", product.identifier, product.price, product.currency)
        state.messages.append(f"Added to cart: {product.identifier} ({product.price} {product.currency})")

    state.buy_state = "CHECKOUT"
    logger.info("[CART] Cart total updated: %.2f", state.cart_total)
    state.messages.append(f"Cart total: {state.cart_total:.2f}")

    logger.debug("[CART] Exit Cart Manager node, updated state: %s", state)
    return state


def order_review_node(state: State) -> State:
    logger.debug("[ORDER_REVIEW] Enter node, current state: %s", state)

    cart_summary = "=== 🛒 CART SUMMARY ==="
    for i, item in enumerate(state.cart, 1):
        cart_summary += f"\n{i}. {item.identifier} - {item.price} {item.currency}"
    cart_summary += f"\n\n💰 Total: {state.cart_total:.2f}"

    checkout_decision = interrupt({
        "target": "checkout_decision",
        "fields": [
            {
                "name": "user_query",
                "prompt": cart_summary + "\n\nQ: Would you like to keep shopping and tell me about another product, or go to checkout?",
                "options": "",
            },
        ],
    })

    user_query = checkout_decision["user_query"].lower().strip()
    if any(x in user_query for x in ['checkout', 'payment']):
        state.buy_state = "PAYMENT"
        state.messages.append("User chose to proceed to PAYMENT.")
        logger.info("[ORDER_REVIEW] User chose to proceed to PAYMENT.")
    else:
        state.buy_state = "SELECT"
        state.user_query = user_query
        state.matched_products.clear()
        state.selected_products.clear()
        state.selected_product_code = ''
        state.messages.append("User chose to continue shopping, selection cleared.")
        logger.info("[ORDER_REVIEW] User chose to continue shopping, selection cleared.")

    logger.debug("[ORDER_REVIEW] Exit node, updated state: %s", state)
    return state
