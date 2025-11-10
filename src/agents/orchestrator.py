# src/agents/orchestrator.py
from langgraph.graph import StateGraph
from src.models.state import State
from src.utils.data_loader import search_by_code, search_by_keyword, identify_product_entity

def orchestrator_node(state: State) -> State:
    query = state.user_query.lower()

    # Heuristic: product code pattern
    is_product_code = query.startswith("yd") and len(query) >= 8
    
    issue_keywords = [
        "issue", "problem", "broken", "not working", "damaged",
        "leaking", "report issue", "doesn't work", "malfunction"
    ]


    if any(word in query for word in ["buy", "order", "part", "need", "want","require"]):
        state.intent = "buy"
        state.messages.append("Intent classified as BUY.")
    elif any(word in query for word in issue_keywords):
        state.intent = "issue"
        state.messages.append("Intent classified as ISSUE.")
    elif is_product_code:
        state.intent = "buy"
        state.messages.append("Intent classified as BUY (product code detected).")
    else:
        state.intent = "unknown"
        state.messages.append("Intent could not be classified.")

    return state


def search_node(state: State, products: list) -> State:
    query = state.user_query.strip()

    if query.upper().startswith("YD"):
        matches = search_by_code(products, query)
        if matches:
            state.matched_products = matches
            state.messages.append(f"Found product by code: {matches[0].identifier}")
        else:
            state.messages.append("No product found for that code.")
    else:
       
        keyword = identify_product_entity(query, products)

        if not keyword:
            state.messages.append("Couldn't identify a product in your query.")
            state.matched_products = []
            return state

        matches = search_by_keyword(products, keyword)
        if matches:
            state.matched_products = matches
            state.messages.append(f"Found {len(matches)} products by keyword: '{keyword}'")
        else:
            state.messages.append(f"No products found for keyword: '{keyword}'")
            state.matched_products = []

    return state
