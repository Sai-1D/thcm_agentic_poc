from src.models.state import State
def controller_node(state: State) -> State:
    return state  # just pass through


def pause_node(state: State) -> State:
    return state

def should_continue(state: State) -> bool:
    # Stop the graph if we're waiting for user input
    if state.intent == "buy" and state.matched_products and not state.selected_product_code:
        return False
    return True



def route_from_controller(state: State) -> str:
    if state.intent == "issue":
        return "issue_reporter"
    elif state.intent == "buy":
        if not state.matched_products:
            return "search"
        elif state.matched_products and not state.selected_products:
            return "pause"  # ⏸️ Wait for user to select product
        elif state.selected_products and not state.cart:
            return "selector"
        elif state.cart and not state.payment_status:
            return "cart_manager"
        elif state.payment_status:
            return "payment"
    return "pause"  # fallback