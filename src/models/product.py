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