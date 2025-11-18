# src/agents/controller.py

from src.models.state import State
from src.utils.logger import logger

def controller_node(state: State) -> State:
    logger.info("[CONTROLLER] Pass-through node, no changes applied.")
    return state  # just pass through

def route_from_controller(state: State) -> str:
    logger.debug("[CONTROLLER] Routing decision, current state: %s", state)

    if state.intent == "issue":
        logger.info("[CONTROLLER] Node selected: issue_reporter")
        return "issue_reporter"
    elif state.intent == "buy":
        if not state.matched_products:
            logger.info("[CONTROLLER] Node selected: search")
            return "search"
        elif not state.selected_product_code:
            logger.info("[CONTROLLER] Node selected: disambiguator")
            return "disambiguator"  # ⏸️ Wait for user to select product
        elif not state.selected_products:
            logger.info("[CONTROLLER] Node selected: selector")
            return "selector"
        elif state.buy_state == 'SELECT':
            logger.info("[CONTROLLER] Node selected: cart_manager")
            return "cart_manager"
        elif state.buy_state == 'CHECKOUT':
            logger.info("[CONTROLLER] Node selected: order_review")
            return "order_review"
        elif state.buy_state == 'PAYMENT':
            logger.info("[CONTROLLER] Node selected: payment")
            return "payment"
        else:
            logger.info("[CONTROLLER] Node selected: end")
            return "end"

    logger.info("[CONTROLLER] Fallback: Node selected: end")
    return "end"  # fallback
