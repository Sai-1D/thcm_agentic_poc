# src/models/quotation.py

from dataclasses import dataclass, field
from typing import List, Optional
from src.models.product import Product
from datetime import datetime
from typing import Optional
import uuid

def generate_quotation_id(prefix: str = "QT") -> str:
    """
    Generates a human-readable, sortable quotation ID.
    Example: QT-20251217-8F3A
    """
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = uuid.uuid4().hex[:4].upper()
    return f"{prefix}-{date_part}-{random_part}"


def current_date_str() -> str:
    """
    Returns date in enterprise-friendly format.
    Example: 17 Dec 2025
    """
    return datetime.now().strftime("%d %b %Y")

# ---------------- Customer ----------------
@dataclass
class CustomerDetails:
    company_name: str
    email: str
    address: str
    phone: str


# ---------------- Shipper / Seller ----------------
@dataclass
class ShipperDetails:
    company_name: str = "Tata Hitachi Construction Machinery"
    address: str = "123 Business Street<br/>Industrial Area<br/>Mumbai, Maharashtra - 400001"
    phone: str = "+91 98765 43210"
    email: str = "sales@tatahitachi.com"
    gstin: Optional[str] = "27AAACY1234D1Z5"
    website: Optional[str] = "www.tatahitachi.com"

# ---------------- Quotation ----------------
@dataclass
class Quotation:
    # -------- REQUIRED FIELDS FIRST --------
    customer: CustomerDetails
    items: List[Product]

    # -------- OPTIONAL / DEFAULT FIELDS --------
    shipper: ShipperDetails = field(default_factory=ShipperDetails)

    quotation_id: str = field(default_factory=generate_quotation_id)
    date: str = field(default_factory=current_date_str)

    tax_percent: float = 18
    currency_symbol: str = "₹"

    notes: Optional[str] = "Prices are indicative and subject to availability."
    terms: List[str] = field(default_factory=lambda: [
        "Payment: 50% advance, balance on delivery.",
        "Validity: 30 days from quotation date.",
        "Prices exclude transportation unless specified.",
    ])

    # -------- Derived values --------
    @property
    def subtotal(self) -> float:
        return sum(item.total_price for item in self.items if item.total_price is not None)

    @property
    def tax_amount(self) -> float:
        return self.subtotal * self.tax_percent / 100

    @property
    def grand_total(self) -> float:
        return self.subtotal + self.tax_amount


# quotation_data = {
#     "quotation_id": "QT-2025-0012",
#     "date": "16 Dec 2025",
#     "customer": {
#         "company_name": "ABC Infra Pvt Ltd",
#         "email": "procurement@abcinfra.com",
#         "address": "Bangalore, Karnataka",
#         "phone": "+91 9384302477"
#     },
#     "shipper": {
#         "company_name": "Tata Hitachi Construction Machinery",
#         "address": "123 Business Street<br/>Industrial Area<br/>Mumbai, Maharashtra - 400001",
#         "phone": "+91 98765 43210",
#         "email": "sales@tatahitachi.com",
#         "gstin": "27AAACY1234D1Z5",
#         "website": "www.tatahitachi.com",
#     },
#     "items": [
#         {"name": "Tata Hitachi EX 210", "article_number": "EX210", "quantity": 1, "unit_price": 5800000},
#         {"name": "Rock Breaker Attachment", "article_number": "RB-210", "quantity": 1, "unit_price": 650000},
#     ],
#     "tax_percent": 18,
#     "currency_symbol": "₹",
#     "notes": "Prices are indicative and subject to availability.",
#     "terms": [
#         "Payment: 50% advance, balance on delivery.",
#         "Validity: 30 days from quotation date.",
#         "Prices exclude transportation unless specified.",
#     ],
# }