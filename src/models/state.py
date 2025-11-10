# src/models/state.py
from dataclasses import dataclass, field
from typing import List, Optional
from src.models.product import Product


@dataclass
class State:
    # User input
    user_query: str = ""
    intent: Optional[str] = None  # buy, issue / unknown (2 possible states for now. Check with Kalyan on the rest)
    selected_product_code: Optional[str] = None  # user-selected article number
    cart: List[Product] = field(default_factory=list)
    cart_total: float = 0.0
    payment_status: Optional[str] = None  # "pending", "authorized", "failed"
    order_id: Optional[str] = None
    card_number: Optional[str] = None
    cvv: Optional[str] = None


    # Product search
    matched_products: List[Product] = field(default_factory=list)
    selected_products: List[Product] = field(default_factory=list)
    # Issue reporting
    issue_description: Optional[str] = None
    issue_ticket_id: Optional[str] = None

    # Logs/messages
    messages: List[str] = field(default_factory=list)