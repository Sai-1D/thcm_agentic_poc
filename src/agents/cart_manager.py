# src/agents/cart_manager.py

import os
from src.models.state import State
from langgraph.types import interrupt
from src.utils.logger import logger
from src.utils.quotation_generator import generate_quotation_pdf
from src.models.quotation_data import CustomerDetails, Quotation
from src.utils.order_review import update_cart

REMOVE_OR_UPDATE_KEYWORDS = ["don't", 'dont', 'not', 'remove', 'delete', "no", "change", "update", "modify", "set"]

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../")
)

QUOTATION_DIR = os.path.join(BASE_DIR, "public", "quotations")

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

    if state.intent == "buy":
        state.buy_state = "ORDER_REVIEW"
    else:  # state.intent == "quotation"
        state.quotation_state = "ORDER_REVIEW"
    logger.info("[CART] Cart total updated: %.2f", state.cart_total)
    state.messages.append(f"Cart total: {state.cart_total:.2f}")

    logger.debug("[CART] Exit Cart Manager node, updated state: %s", state)
    return state


def order_review_node(state: State) -> State:
    logger.debug("[ORDER_REVIEW] Enter node, current state: %s", state)

    cart_summary = ""
    if state.buy_state == "ORDER_REVIEW" or state.quotation_state == "ORDER_REVIEW":
        cart_summary += "=== 🛒 CART SUMMARY ==="
    else:
        cart_summary += "=== 🛒 UPDATED CART SUMMARY ==="
    
    for i, item in enumerate(state.cart, 1):
        cart_summary += f"\n{i}. {item.article_number} | {item.identifier} | {item.price} {item.currency} | Qty {item.quantity}"
    
    logger.info(f'{state.buy_state}, {state.quotation_state}')
    cart_summary += f"\n\n**note: {state.messages[-1]}" if state.buy_state == "UPDATION" or state.quotation_state == "UPDATION" else ""

    if state.intent == "buy":
        if len(state.cart) == 0:
            user_query = interrupt({
                "target": "user_query",
                "fields": [
                    {
                        "name": "user_query",
                        "prompt": cart_summary + "\n\nI: Your cart is empty right now.\nQ: Please browse products to add items before moving ahead with quotation or checkout.",
                        "options": "",
                    },
                ],
            })
            user_query = user_query["user_query"].lower().strip()
            state.buy_state = "SELECT"
            state.user_query = user_query
            state.matched_products.clear()
            state.selected_products.clear()
            state.selected_product_code = ''
            state.messages.append("User chose to continue shopping, selection cleared.")
            logger.info("[ORDER_REVIEW] User chose to continue shopping, selection cleared.")

            return state
        
        checkout_decision = interrupt({
            "target": "checkout_decision",
            "fields": [
                {
                    "name": "user_query",
                    "prompt": cart_summary + "\n\nQ: What would you like to do next?\nI: You can continue browsing, request a quotation for these items, or move ahead with checkout.",
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
        elif any(x in user_query for x in REMOVE_OR_UPDATE_KEYWORDS):
            state = update_cart(user_query, state)
            state.buy_state = "UPDATION"
            logger.info("[ORDER_REVIEW] User chose to proceed to ORDER_REVIEW.")
        else:
            state.buy_state = "SELECT"
            state.user_query = user_query
            state.matched_products.clear()
            state.selected_products.clear()
            state.selected_product_code = ''
            state.messages.append("User chose to continue shopping, selection cleared.")
            logger.info("[ORDER_REVIEW] User chose to continue shopping, selection cleared.")

    elif state.intent == "quotation":
        if len(state.cart) == 0:
            user_query = interrupt({
                "target": "user_query",
                "fields": [
                    {
                        "name": "user_query",
                        "prompt": cart_summary + "\n\nI: Your cart is empty right now.\nQ: Please browse products to add items before proceeding with quotation.",
                        "options": "",
                    },
                ],
            })
            user_query = user_query["user_query"].lower().strip()
            state.quotation_state = "SELECT"
            state.user_query = user_query
            state.matched_products.clear()
            state.selected_products.clear()
            state.selected_product_code = ''
            state.messages.append("User chose to continue shopping, selection cleared.")
            logger.info("[ORDER_REVIEW] User chose to continue shopping, selection cleared.")

        else:
            quotation_decision = interrupt({
                "target": "quotation_decision",
                "fields": [
                    {
                        "name": "user_query",
                        "prompt": cart_summary + "\n\nQ: What would you like to do next?\nI: Feel free to browse more products or move ahead with the quotation.",
                        "options": "",
                    },
                ],
            })
            user_query = quotation_decision["user_query"].lower().strip()
            if any(x in user_query for x in ['quotation']):
                state.quotation_state = "QUOTATION"
                state.messages.append("User chose to proceed to QUOTATION.")
                logger.info("[ORDER_REVIEW] User chose to proceed to QUOTATION.")
            elif any(x in user_query for x in REMOVE_OR_UPDATE_KEYWORDS):
                state = update_cart(user_query, state)
                state.quotation_state = "UPDATION"
                logger.info("[ORDER_REVIEW] User chose to proceed to ORDER_REVIEW.")
            else:
                state.quotation_state = "SELECT"
                state.user_query = user_query
                state.matched_products.clear()
                state.selected_products.clear()
                state.selected_product_code = ''
                state.messages.append("User chose to continue shopping, selection cleared.")
                logger.info("[ORDER_REVIEW] User chose to continue shopping, selection cleared.")

    logger.debug("[ORDER_REVIEW] Exit node, updated state: %s", state)
    return state

def quotation_node(state: State, config) -> State:
    logger.debug("[QUOTATION] Enter Quotation node, current state: %s", state)

    # if not state.user_or_company_name:
    #     user_or_company_name_val = interrupt({
    #         "target": "user_or_company_name",
    #         "fields": [
    #             {
    #                 "name": "user_or_company_name",
    #                 "prompt": "Q: I’m getting your quotation ready. Could you please share your name or company name?",
    #                 "options": "",
    #             },
    #         ],
    #     })
    #     state.user_or_company_name = user_or_company_name_val["user_or_company_name"].strip()
    
    # if not state.user_or_company_mail:
    #     user_or_company_mail_val = interrupt({
    #         "target": "user_or_company_mail",
    #         "fields": [
    #             {
    #                 "name": "user_or_company_mail",
    #                 "prompt": "\nQ: Please share your email or company email where I can send the quotation.",
    #                 "options": "",
    #             },
    #         ],
    #     })
    #     state.user_or_company_mail = user_or_company_mail_val["user_or_company_mail"].strip()
    
    # if not state.user_or_company_address:
    #     user_or_company_address_val = interrupt({
    #         "target": "user_or_company_address",
    #         "fields": [
    #             {
    #                 "name": "user_or_company_address",
    #                 "prompt": "\nQ: Please share your billing or company address for the quotation.",
    #                 "options": "",
    #             },
    #         ],
    #     })
    #     state.user_or_company_address = user_or_company_address_val["user_or_company_address"].strip()
    
    state.user_or_company_name = "User 1"
    state.user_or_company_mail = "user1@example.com"
    state.user_or_company_address = "Address 1, City 1, State 1, Pincode 1"
    quotation_data = Quotation(customer=CustomerDetails(company_name=state.user_or_company_name,
                                                        email=state.user_or_company_mail,
                                                        address=state.user_or_company_address, 
                                                        phone="+91 9384397477"),
                                items = state.cart)
    pdf_bytes = generate_quotation_pdf(quotation=quotation_data)
    thread_id = config["configurable"].get("thread_id")

    with open(f"{QUOTATION_DIR}/quotation_{thread_id}.pdf", "wb") as f:
        f.write(pdf_bytes)

    logger.debug("[QUOTATION] Exit Quotation node, updated state: %s", state)
    return state
