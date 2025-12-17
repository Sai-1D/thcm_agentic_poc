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

    state.buy_state = "ORDER_REVIEW"
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
                "prompt": cart_summary + "\n\nWhat would you like to do next?\n You can continue browsing, request a quotation for these items, or move ahead with checkout.",
                "options": "",
            },
        ],
    })

    user_query = checkout_decision["user_query"].lower().strip()
    if any(x in user_query for x in ['checkout', 'payment']):
        state.buy_state = "PAYMENT"
        state.messages.append("User chose to proceed to PAYMENT.")
        logger.info("[ORDER_REVIEW] User chose to proceed to PAYMENT.")
    elif any(x in user_query for x in ['quotation']):
        state.buy_state = "QUOTATION"
        state.messages.append("User chose to proceed to QUOTATION.")
        logger.info("[ORDER_REVIEW] User chose to proceed to QUOTATION.")
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

def quotation_node(state: State) -> State:
    logger.debug("[QUOTATION] Enter Quotation node, current state: %s", state)

    if not state.user_or_company_name:
        user_or_company_name_val = interrupt({
            "target": "user_or_company_name",
            "fields": [
                {
                    "name": "user_or_company_name",
                    "prompt": "Before I prepare the quotation, I’ll need a few details.\n\nPlease share your name or company name.",
                    "options": "",
                },
            ],
        })
        state.user_or_company_name = user_or_company_name_val["user_or_company_name"].strip()
    
    if not state.user_or_company_mail:
        user_or_company_mail_val = interrupt({
            "target": "user_or_company_mail",
            "fields": [
                {
                    "name": "user_or_company_mail",
                    "prompt": "\nPlease share your email or company email where I can send the quotation.",
                    "options": "",
                },
            ],
        })
        state.user_or_company_mail = user_or_company_mail_val["user_or_company_mail"].strip()
    
    if not state.user_or_company_address:
        user_or_company_address_val = interrupt({
            "target": "user_or_company_address",
            "fields": [
                {
                    "name": "user_or_company_address",
                    "prompt": "\nPPlease share your billing or company address for the quotation.",
                    "options": "",
                },
            ],
        })
        state.user_or_company_address = user_or_company_address_val["user_or_company_address"].strip()

    logger.debug("[QUOTATION] Exit Quotation node, updated state: %s", state)
    return state