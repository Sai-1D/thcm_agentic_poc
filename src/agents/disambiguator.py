# src/agents/disambiguator.py
from src.models.state import State
from langgraph.types import interrupt
from src.utils.logger import logger

def disambiguator_node(state: State) -> State:
    logger.debug("[DISAMBIGUATOR_NODE] Start: %s", state)
    matches = state.matched_products

    if len(matches) <= 1:
        state.selected_product_code = matches[0].article_number
        state.selected_products = matches
        state.messages.append("No disambiguation needed.")
        logger.info("[DISAMBIGUATOR_NODE] No disambiguation needed, auto-selected product: %s", matches[0].identifier)
        logger.info("[DISAMBIGUATOR_NODE] End: %s", state)
        return state

    # Show top 3 matches
    match_summary = "=== 🔍 PRODUCT MATCHES ==="
    for i, p in enumerate(matches[:3]):
        match_summary += f"\n{i+1}. {p.identifier} - {p.price} {p.currency} (Article No: {p.article_number})"

    match_prompt = match_summary + "\n\nQ: Please enter the article number of the product you’d like to select."

    state.messages.append(f"Multiple products matched your query:\n{match_summary}")
    logger.info("[DISAMBIGUATOR_NODE] Multiple matches found:")
    logger.debug(f"[DISAMBIGUATOR_NODE] Multiple matches found:\n{match_summary}")

    selection_details = interrupt({
        "target": "product_selection",
        "fields": [
            {"name": "article_number", "prompt": match_prompt, "options": ''},
        ],
    })

    state.selected_product_code = selection_details.get('article_number')
    logger.info("[DISAMBIGUATOR_NODE] User selected article number: %s", state.selected_product_code)
    logger.debug("[DISAMBIGUATOR_NODE] End: %s", state)
    return state


def selector_node(state: State) -> State:
    logger.debug("[SELECTOR_NODE] Start: %s", state)
    code = state.selected_product_code

    if not code:
        state.messages.append("No product selected.")
        logger.warning("[SELECTOR_NODE] No product selected by user.")
        logger.info("[SELECTOR_NODE] End: %s", state)
        return state

    selected = [p for p in state.matched_products if p.article_number.lower() == code.lower()]
    if selected:
        state.selected_products = selected
        state.messages.append(f"Selected product: {selected[0].identifier}")
        logger.info("[SELECTOR_NODE] Product selected: %s", selected[0].identifier)
    else:
        state.messages.append("Invalid selection. No matching product found.")
        logger.warning("[SELECTOR_NODE] Invalid selection: %s", code)

    logger.debug("[SELECTOR_NODE] End: %s", state)
    return state
