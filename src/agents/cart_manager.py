# src/agents/cart_manager.py
from src.models.state import State
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

    state.selected_products.clear()
    logger.info("[CART] Cart total updated: %.2f", state.cart_total)
    state.messages.append(f"Cart total: {state.cart_total:.2f}")

    logger.debug("[CART] Exit Cart Manager node, updated state: %s", state)
    return state
