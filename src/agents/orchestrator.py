# src/agents/orchestrator.py

from langgraph.graph import StateGraph, END
from src.models.state import State
from src.utils.data_loader import search_by_code, search_by_keyword, identify_product_entity
from langgraph.types import Command
from src.utils.logger import logger

def orchestrator_node(state: State) -> State:
    logger.debug("[ORCHESTRATOR_NODE] Start: %s", state)

    query = state.user_query.lower()

    # Heuristic: product code pattern
    is_product_code = query.startswith("yd") and len(query) >= 8
    
    buy_keywords = [
        "buy", "order", "part", "need", "want", "require"
    ]
    issue_keywords = [
        "issue", "problem", "broken", "not working", "damaged",
        "leaking", "report issue", "doesn't work", "malfunction"
    ]

    if any(word in query for word in buy_keywords):
        state.intent = "buy"
        state.messages.append("Intent classified as BUY.")
        logger.info("[ORCHESTRATOR_NODE] Intent classified as BUY for query='%s'", query)
    elif any(word in query for word in issue_keywords):
        state.intent = "issue"
        state.messages.append("Intent classified as ISSUE.")
        logger.info("[ORCHESTRATOR_NODE] Intent classified as ISSUE for query='%s'", query)
    elif is_product_code:
        state.intent = "buy"
        state.messages.append("Intent classified as BUY (product code detected).")
        logger.info("[ORCHESTRATOR_NODE] Intent classified as BUY (product code) for query='%s'", query)
    else:
        state.intent = "unknown"
        state.messages.append("Intent could not be classified.")
        logger.warning("[ORCHESTRATOR_NODE] Intent UNKNOWN for query='%s'", query)

    logger.debug("[ORCHESTRATOR_NODE] End: %s", state)
    return state


def search_node(state: State, products: list) -> Command:
    logger.debug("[SEARCH_NODE] Start: %s", state)

    query = state.user_query.strip()

    if query.upper().startswith("YD"):
        matches = search_by_code(products, query)
        if matches:
            state.matched_products = matches
            state.messages.append(f"Found product by code: {matches[0].identifier}")
            goto = "controller"
            logger.info("[SEARCH_NODE] Found product by code: %s", matches[0].identifier)
        else:
            state.messages.append("No product found for that code.")
            goto = END
            logger.info("[SEARCH_NODE] No product found for code: %s", query)

    else:
        keyword = identify_product_entity(query, products)

        if not keyword:
            state.messages.append("Couldn't identify a product in your query.")
            state.matched_products = []
            goto = END
            logger.info("[SEARCH_NODE] Couldn't identify any keyword in query: %s", query)

        matches = search_by_keyword(products, keyword)
        if matches:
            state.matched_products = matches
            state.messages.append(f"Found {len(matches)} products by keyword: '{keyword}'")
            goto = "controller"
            logger.info("[SEARCH_NODE] Found %d products for keyword: '%s'", len(matches), keyword)
        else:
            state.messages.append(f"No products found for keyword: '{keyword}'")
            state.matched_products = []
            goto = END
            logger.info("[SEARCH_NODE] No products found for keyword: '%s'", keyword)

    logger.debug("[SEARCH_NODE] End: %s", state)
    return Command(goto=goto, update=state)