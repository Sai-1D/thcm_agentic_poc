# src/models/product.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class Product:
    article_number: str
    description: Optional[str]
    identifier: str
    keywords: list[str]
    price: Optional[float]
    currency: Optional[str]
    unit: Optional[str]
    product_type: Optional[str]
    quantity: int = 1

    @property
    def total_price(self) -> Optional[float]:
        if self.price is None:
            return None
        if self.quantity <= 0:
            return None
        try:
            return self.quantity * float(self.price)
        except (TypeError, ValueError):
            return None