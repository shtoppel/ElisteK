from app.db import repo

EGGS_ID = 54

def calc_step(product_id: int, unit_type: str, category: str, mode: str) -> float:
    unit_type = (unit_type or "").lower()
    category = (category or "").lower()

    if product_id == EGGS_ID and mode == "menu":
        return 10.0

    if unit_type in {"pcs", "st", "st.", "шт"}:
        return 1.0

    if unit_type == "kg":
        return 0.5 if mode == "menu" else 0.25

    if unit_type in {"liter", "l"} or category == "drinks":
        return 1.0 if mode == "menu" else 0.5

    return 1.0

def change_item_qty(user_id: int, product_id: int, is_plus: bool, mode: str) -> None:
    meta = repo.get_product_meta(product_id)
    if not meta:
        return
    unit_type, category, _name = meta

    step = calc_step(product_id, unit_type, category, mode)
    current = repo.get_cart_qty(user_id, product_id)
    new_qty = round(current + step, 2) if is_plus else round(current - step, 2)
    repo.upsert_cart_qty(user_id, product_id, new_qty)

def build_finish_report(cart_items) -> str:
    bought_text, skipped_text = "", ""
    for item in cart_items:
        p_id, name, emoji, qty, status, unit_type, _cat = item
        if status == -1:
            continue

        u_name = "kg" if unit_type == "kg" else "l" if unit_type == "liter" else "st"
        display_qty = int(qty) if qty % 1 == 0 else qty
        line = f"• {emoji} {name} — {display_qty} {u_name}\n"

        if status == 1:
            bought_text += line
        else:
            skipped_text += line

    report = "🏁 *Der Kauf ist abgeschlossen!*\n\n"
    if bought_text:
        report += "✅ *Gekauft:*\n" + bought_text + "\n"
    if skipped_text:
        report += "❌ *Nicht gekauft:*\n" + skipped_text
    return report