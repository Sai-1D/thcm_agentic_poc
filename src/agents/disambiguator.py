# src/agents/disambiguator.py
from src.models.state import State

def disambiguator_node(state: State) -> State:
    matches = state.matched_products
    if len(matches) <= 1:
        state.messages.append("No disambiguation needed.")
        return state

    # Show top 3 matches
    summary = "\n".join(
        f"{i+1}. {p.article_number} - {p.identifier} ({p.price} {p.currency})"
        for i, p in enumerate(matches[:3])
    )
    state.messages.append(f"Multiple products matched your query:\n{summary}")
    state.messages.append("Please enter the article number of the product you want to select.")
    return state

    
def selector_node(state: State) -> State:
    code = state.selected_product_code
    if not code:
        state.messages.append("No product selected.")
        return state

    selected = [p for p in state.matched_products if p.article_number.lower() == code.lower()]
    if selected:
        state.selected_products = selected
        state.messages.append(f"Selected product: {selected[0].identifier}")
    else:
        state.messages.append("Invalid selection. No matching product found.")
    return state