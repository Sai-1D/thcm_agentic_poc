# src/models/state.py

from dataclasses import dataclass, field
from typing import List, Optional
from src.models.product import Product

@dataclass
class State:
    user_query: str = ""  # User input
    intent: Optional[str] = None  # buy, issue / unknown (2 possible states for now. Check with Kalyan on the rest)
    buy_state: str = "SELECT" # SELECT or CHECKOUT or PAYMENT or Quotation

    # Product search
    matched_products: List[Product] = field(default_factory=list)
    selected_products: List[Product] = field(default_factory=list)
    selected_product_code: Optional[str] = None  # user-selected article number

    # User Data for quotation
    user_or_company_name: Optional[str] = None
    user_or_company_address: Optional[str] = None
    user_or_company_mail: Optional[str] = None

    # checkout
    cart: List[Product] = field(default_factory=list)
    cart_total: float = 0.0
    order_id: Optional[str] = None
    payment_status: Optional[str] = None  # "pending", "authorized", "failed"

    # Issue reporting
    issue_description: Optional[str] = None
    issue_ticket_id: Optional[str] = None

    # Logs/messages
    messages: List[str] = field(default_factory=list)