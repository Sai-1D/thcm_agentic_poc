# src/utils/order_review.py

import re
from src.models.state import State
from typing import Optional
from src.utils.logger import logger

REMOVE_KEYWORDS = {"remove", "delete", "dont", "don't", "not", "no"}
UPDATE_KEYWORDS = {"change", "update", "modify", "set"}

def extract_quantity(text: str) -> Optional[int]:
    """
    Extracts the first integer found in text.
    Returns None if no valid quantity is found.
    """
    match = re.search(r"\b\d+\b", text)
    if not match:
        return None

    qty = int(match.group())
    return qty if qty > 0 else None

def update_cart(user_query: str, state: State) -> State:
    user_query_lower = user_query.lower()

    product_to_update = [
        p for p in state.cart
        if p.article_number.lower() in user_query_lower
        or p.identifier.lower() in user_query_lower
    ]

    if not product_to_update:
        state.messages.append(
            "I couldn’t find that product in your cart."
        )
        logger.info(
            "[ORDER_REVIEW] No matching product found in cart for query: '%s'",
            user_query,
        )
        return state

    product = product_to_update[0]

    # ---------- REMOVE ----------
    if any(word in user_query_lower for word in REMOVE_KEYWORDS):
        state.cart = [
            p for p in state.cart
            if p.article_number != product.article_number
        ]
        state.messages.append(
            f"Removed {product.identifier} from your cart."
        )
        logger.info(
            "[ORDER_REVIEW] Removed product '%s' (article_number=%s) from cart",
            product.identifier,
            product.article_number,
        )

        return state

    # ---------- UPDATE QUANTITY ----------
    new_qty = extract_quantity(user_query)

    if new_qty is not None:
        product.quantity = new_qty
        state.messages.append(
            f"Updated {product.identifier} quantity to {new_qty}."
        )
        logger.info(
            "[ORDER_REVIEW] Updated quantity for product '%s' (article_number=%s) to %d",
            product.identifier,
            product.article_number,
            new_qty,
        )
        return state

    # ---------- FALLBACK ----------
    state.messages.append(
        f"Couldn’t understand the update for {product.identifier}. "
    )
    logger.warning(
        "[ORDER_REVIEW] Unable to interpret cart update request for product '%s' (article_number=%s)",
        product.identifier,
        product.article_number,
    )
    return state