# src/utils/data_loader.py
import pandas as pd
import re
import os
from src.models.product import Product
from difflib import get_close_matches


def parse_price_details(raw_price: str) -> tuple[float | None, str, str]:
    raw_price = raw_price.strip()
    match = re.search(r"(\d+(\.\d+)?)\s*([A-Z]+)?[:]?[:]?.*?(\bEA\b|\bPC\b|\bSET\b)?", raw_price)
    if match:
        price = float(match.group(1))
        currency = match.group(3) or ""
        unit = match.group(4) or ""
        return price, currency, unit
    return None, "", ""

def load_catalog(path: str) -> list[Product]:
    # Use absolute path if needed
    path = os.path.abspath(path)
    print("Loading catalog from:", path)

    # Load Excel sheet
    df = pd.read_excel(path, sheet_name="products").fillna("")
    print("Catalog loaded:", len(df))

    products = []
    for _, row in df.iterrows():
        raw_price = str(row["Price"])
        price, currency, unit = parse_price_details(raw_price)

        product = Product(
            article_number=str(row["Article Number"]).strip(),
            description=str(row["Description"]).strip(),
            identifier=str(row["Identifier"]).strip().replace(";", " - "),
            keywords=[str(k).strip() for k in str(row["Keywords"]).split(",") if k],
            price=price,
            currency=currency,
            unit=unit,
            product_type=str(row["productType"]).strip()
        )
        products.append(product)

    print("Products loaded:", len(products))
    return products



def build_product_terms(products: list[Product]) -> set:
    terms = set()
    for p in products:
        terms.add(p.identifier.lower())
        terms.update(k.lower() for k in p.keywords)
        if p.description:
            terms.add(p.description.lower())
    return terms

def extract_candidate_tokens(query: str) -> list:
    query = query.lower()
    tokens = re.findall(r'\b\w+\b', query)
    return tokens

def identify_product_entity(query: str, products: list) -> str | None:
    query = query.lower()
    tokens = re.findall(r'\b\w+\b', query)

    # Ignore common stopwords
    stopwords = {"i", "want", "to", "buy", "a", "need", "order", "please", "can"}
    meaningful_tokens = [t for t in tokens if t not in stopwords]

    if not meaningful_tokens:
        return None

    # Score each token by how many products it matches
    token_scores = {}
    for token in meaningful_tokens:
        count = 0
        for product in products:
            fields = [
                product.identifier.lower() if product.identifier else "",
                product.description.lower() if product.description else "",
                " ".join(k.lower() for k in product.keywords if k)
            ]
            combined = " ".join(fields)
            if token in combined:
                count += 1
        token_scores[token] = count

    if not token_scores:
        return None

    # Pick the token with the highest score
    best_token = max(token_scores, key=token_scores.get)
    print(f"Looking up for keyword: {best_token}")
    return best_token





def search_by_code(products: list[Product], code: str) -> list[Product]:
    return [p for p in products if p.article_number.lower() == code.lower()]

def search_by_keyword(products: list, keyword: str) -> list:
    keyword = keyword.lower()
    matches = []
    print("Looking up for keyword: "+keyword);

    for product in products:
        if (
            keyword in product.description.lower()
            or keyword in product.identifier.lower()
            or any(keyword in k.lower() for k in product.keywords)
        ):
            matches.append(product)

    return matches
