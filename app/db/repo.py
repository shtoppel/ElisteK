from __future__ import annotations
from typing import Optional, Tuple, List
from .schema import connect

# (id, name, emoji, qty, is_bought, unit_type, category)
CartItem = Tuple[int, str, str, float, int, str, str]

def get_products_by_cat(category_code: str):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT id, name, emoji, unit_type FROM products WHERE category = ?", (category_code,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_cart_items(user_id: int) -> List[CartItem]:
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, p.name, p.emoji, c.quantity, c.is_bought, p.unit_type, p.category
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ? AND c.is_bought != -1
        ORDER BY p.category ASC, p.name ASC
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def clear_cart(user_id: int) -> None:
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def toggle_bought_status(user_id: int, product_id: int) -> None:
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "UPDATE cart SET is_bought = 1 - is_bought WHERE user_id = ? AND product_id = ?",
        (user_id, product_id)
    )
    conn.commit()
    conn.close()

def mark_deleted(user_id: int, product_id: int) -> None:
    conn = connect()
    cur = conn.cursor()
    cur.execute("UPDATE cart SET is_bought = -1 WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    conn.commit()
    conn.close()

def save_to_history_and_clear(user_id: int) -> None:
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO purchase_history (user_id, product_name, quantity, date)
        SELECT c.user_id, p.name, c.quantity, datetime('now')
        FROM cart c JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ? AND c.is_bought = 1
    """, (user_id,))

    cur.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_category_by_id(product_id: int) -> Optional[str]:
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT category FROM products WHERE id = ?", (product_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def get_product_meta(product_id: int) -> Optional[Tuple[str, str, str]]:
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT unit_type, category, name FROM products WHERE id = ?", (product_id,))
    row = cur.fetchone()
    conn.close()
    return (row[0], row[1], row[2]) if row else None

def get_cart_qty(user_id: int, product_id: int) -> float:
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT quantity, is_bought FROM cart WHERE user_id = ? AND product_id = ?",
        (user_id, product_id)
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return 0.0

    qty, is_bought = row

    if is_bought == -1:
        return 0.0

    return float(qty)

def upsert_cart_qty(user_id: int, product_id: int, new_qty: float) -> None:
    conn = connect()
    cur = conn.cursor()

    # Exists?
    cur.execute("SELECT is_bought FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    row = cur.fetchone()

    if new_qty <= 0:
        cur.execute("DELETE FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    else:
        if row:
            # ✅ revive if previously removed (-1)
            cur.execute("""
                UPDATE cart
                SET quantity = ?,
                    is_bought = CASE WHEN is_bought = -1 THEN 0 ELSE is_bought END
                WHERE user_id = ? AND product_id = ?
            """, (new_qty, user_id, product_id))
        else:
            cur.execute(
                "INSERT INTO cart (user_id, product_id, quantity, is_bought) VALUES (?, ?, ?, 0)",
                (user_id, product_id, new_qty)
            )

    conn.commit()
    conn.close()
def update_product_unit_type(product_id: int, unit_type: str) -> None:
    conn = connect()
    cur = conn.cursor()
    cur.execute("UPDATE products SET unit_type = ? WHERE id = ?", (unit_type, product_id))
    conn.commit()
    conn.close()

def get_all_products_id_name():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM products")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_or_create_custom_product(item_name: str, unit_type: str = "st", emoji: str = "📝") -> int:
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT id FROM products WHERE name = ? AND category = 'other'", (item_name,))
    row = cur.fetchone()
    if row:
        product_id = row[0]
    else:
        cur.execute(
            "INSERT INTO products (name, category, emoji, unit_type) VALUES (?, 'other', ?, ?)",
            (item_name, emoji, unit_type)
        )
        product_id = cur.lastrowid

    conn.commit()
    conn.close()
    return int(product_id)