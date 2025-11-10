# src/agents/cart_manager.py
from src.models.state import State

def cart_manager_node(state: State) -> State:
    if not state.selected_products:
        state.messages.append("No product selected to add to cart.")
        return state

    for product in state.selected_products:
        state.cart.append(product)
        if product.price:
            state.cart_total += product.price
        state.messages.append(f"Added to cart: {product.identifier} ({product.price} {product.currency})")

    state.selected_products.clear()
    state.messages.append(f"Cart total: {state.cart_total:.2f}")
    return state