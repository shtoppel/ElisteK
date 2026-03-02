from thefuzz import process, fuzz
from app.db import repo

def find_product_smart(user_input: str):
    all_products = repo.get_all_products_id_name()

    for p_id, p_name in all_products:
        if p_name.lower() == user_input.lower():
            return p_id

    names = [p[1] for p in all_products]
    best = process.extractOne(user_input, names, scorer=fuzz.WRatio)
    if not best:
        return None

    best_match, score = best
    if score > 80:
        for p_id, p_name in all_products:
            if p_name == best_match:
                return p_id
    return None

def add_to_cart_smart(user_id: int, product_id: int, quantity: float = 1.0):
    current = repo.get_cart_qty(user_id, product_id)
    repo.upsert_cart_qty(user_id, product_id, round(current + float(quantity), 2))

def add_unknown_to_cart(user_id: int, item_name: str, quantity: float = 1.0, unit_type: str = "st"):
    product_id = repo.get_or_create_custom_product(item_name, unit_type=unit_type)
    add_to_cart_smart(user_id, product_id, quantity)