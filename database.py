import sqlite3
from thefuzz import process, fuzz
import os

DB_NAME = os.getenv("DB_PATH", "shop.db")

# --- SPECIAL IDS ---
EGGS_ID = 54


def init_db():
    """Initializes the database and populates the products table if empty."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. Products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT, 
        category TEXT, 
        emoji TEXT,
        unit_type TEXT DEFAULT 'pcs',
        price FLOAT DEFAULT 0.0
    )""")

    # 2. Shopping cart table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cart (
        user_id INTEGER, 
        product_id INTEGER, 
        quantity REAL DEFAULT 0,
        is_bought INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, product_id)
    )""")

    # 3. Purchase history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS purchase_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_name TEXT,
        quantity REAL,
        price FLOAT,
        date TEXT
    )""")

    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        items = [
            # VEGETABLES 🥦
            (1, 'Kartoffeln', 'veg', '🥔', 'kg'), (2, 'Tomaten', 'veg', '🍅', 'kg'),
            (3, 'Gurken', 'veg', '🥒', 'pcs'), (4, 'Zwiebeln', 'veg', '🧅', 'kg'),
            (5, 'Karotten', 'veg', '🥕', 'kg'), (6, 'Paprika', 'veg', '👝', 'kg'),
            (7, 'Knoblauch', 'veg', '🧄', 'pcs'), (8, 'Brokkoli', 'veg', '🥦', 'pcs'),
            (9, 'Blumenkohl', 'veg', '🥦', 'pcs'), (10, 'Salat', 'veg', '🥬', 'pcs'),
            (11, 'Zucchini', 'veg', '🥒', 'kg'), (12, 'Aubergine', 'veg', '🍆', 'pcs'),
            (13, 'Pilze', 'veg', '🍄', 'kg'), (14, 'Ingwer', 'veg', '🫚', 'kg'),
            (15, 'Avocado', 'veg', '🥑', 'pcs'), (16, 'Spinat', 'veg', '🍃', 'pcs'),

            # FRUITS 🍎
            (17, 'Äpfel', 'fruits', '🍎', 'kg'), (18, 'Bananen', 'fruits', '🍌', 'kg'),
            (19, 'Orangen', 'fruits', '🍊', 'kg'), (20, 'Zitronen', 'fruits', '🍋', 'pcs'),
            (21, 'Weintrauben', 'fruits', '🍇', 'kg'), (22, 'Erdbeeren', 'fruits', '🍓', 'pcs'),
            (23, 'Blaubeeren', 'fruits', '🫐', 'pcs'), (24, 'Himbeeren', 'fruits', '🍒', 'pcs'),
            (25, 'Birnen', 'fruits', '🍐', 'kg'), (26, 'Pfirsiche', 'fruits', '🍑', 'kg'),
            (27, 'Kiwi', 'fruits', '🥝', 'pcs'), (28, 'Ananas', 'fruits', '🍍', 'pcs'),
            (29, 'Melone', 'fruits', '🍉', 'pcs'), (30, 'Mango', 'fruits', '🥭', 'pcs'),

            # MEAT & SAUSAGE 🥩
            (31, 'Hähnchenbrust', 'meat', '🍗', 'kg'), (32, 'Rindfleisch', 'meat', '🥩', 'kg'),
            (33, 'Schweinefleisch', 'meat', '🍖', 'kg'), (34, 'Hackfleisch', 'meat', '🥘', 'kg'),
            (35, 'Schinken', 'meat', '🥓', 'kg'), (36, 'Salami', 'meat', '🍕', 'pcs'),
            (37, 'Würstchen', 'meat', '🌭', 'pcs'), (38, 'Putenfleisch', 'meat', '🦃', 'kg'),
            (39, 'Lachs', 'meat', '🐟', 'kg'), (40, 'Garnelen', 'meat', '🍤', 'kg'),

            # BAKERY 🥐
            (41, 'Weißbrot', 'bakery', '🍞', 'pcs'), (42, 'Baguette', 'bakery', '🥖', 'pcs'),
            (43, 'Brötchen', 'bakery', '🥐', 'pcs'), (44, 'Toastbrot', 'bakery', '🥪', 'pcs'),
            (45, 'Vollkornbrot', 'bakery', '🍞', 'pcs'), (46, 'Brezel', 'bakery', '🥨', 'pcs'),
            (47, 'Croissant', 'bakery', '🥐', 'pcs'), (48, 'Kuchen', 'bakery', '🍰', 'pcs'),

            # DAIRY 🥛
            (49, 'Milch', 'dairy', '🥛', 'liter'), (50, 'Quark', 'dairy', '⚪', 'pcs'),
            (51, 'Käse', 'dairy', '🧀', 'kg'), (52, 'Sahne', 'dairy', '🍶', 'pcs'),
            (53, 'Butter', 'dairy', '🧈', 'pcs'), (54, 'Eier', 'dairy', '🥚', 'pcs'),
            (55, 'Joghurt', 'dairy', '🍦', 'pcs'), (56, 'Frischkäse', 'dairy', '🥣', 'pcs'),
            (57, 'Schmand', 'dairy', '🥛', 'pcs'), (58, 'Kefir', 'dairy', '🥤', 'liter'),

            # DRINKS 🥤
            (59, 'Mineralwasser', 'drinks', '💧', 'pcs'), (60, 'Saft', 'drinks', '🧃', 'liter'),
            (61, 'Cola', 'drinks', '🥤', 'liter'), (62, 'Bier', 'drinks', '🍺', 'liter'),
            (63, 'Kaffee', 'drinks', '☕', 'pcs'), (64, 'Tee', 'drinks', '🫖', 'pcs'),
            (65, 'Wein', 'drinks', '🍷', 'liter'), (66, 'Eistee', 'drinks', '🍹', 'liter'),

            # SWEETS 🍫
            (67, 'Schokolade', 'sweets', '🍫', 'pcs'), (68, 'Kekse', 'sweets', '🍪', 'kg'),
            (69, 'Gummibärchen', 'sweets', '🍬', 'pcs'), (70, 'Eiscreme', 'sweets', '🍦', 'pcs'),
            (71, 'Chips', 'sweets', '🥔', 'pcs'), (72, 'Nüsse', 'sweets', '🥜', 'kg'),
            (73, 'Honig', 'sweets', '🍯', 'pcs'), (74, 'Marmelade', 'sweets', '🍓', 'pcs'),

            # HYGIENE 🧼
            (75, 'Seife', 'hygiene', '🧼', 'pcs'), (76, 'Shampoo', 'hygiene', '🧴', 'pcs'),
            (77, 'Zahnpasta', 'hygiene', '🪥', 'pcs'), (78, 'Toilettenpapier', 'hygiene', '🧻', 'pcs'),
            (79, 'Waschmittel', 'hygiene', '🧺', 'pcs'), (80, 'Küchenrollen', 'hygiene', '🧻', 'pcs'),
            (81, 'Duschgel', 'hygiene', '🚿', 'pcs'), (82, 'Deo', 'hygiene', '🌬️', 'pcs'),

            # FROZEN FOOD ❄️
            (83, 'Pelmeni', 'tiefkühlkost', '🥟', 'kg'), (84, 'Pizza', 'tiefkühlkost', '🍕', 'st'),
            (85, 'Pommes', 'tiefkühlkost', '🍟', 'kg'), (86, 'Nuggets', 'tiefkühlkost', '🥡', 'kg'),
            (87, 'Burger', 'tiefkühlkost', '🍔', 'st'),

            # CANNED FOOD 🥫
            (88, 'Thunfisch', 'konserven', '🫙', 'st'),
            (89, 'Dose Erbsen', 'konserven', '🫛', 'st'),
            (90, 'Dosenmais', 'konserven', '🌽', 'st'),
            (91, 'Gewürzgurken', 'konserven', '🥒', 'st'),
            (92, 'Konservierte Tomaten', 'konserven', '🥫', 'st'),
            (93, 'Oliven', 'konserven', '🫒', 'st'),
            (94, 'Sprotten', 'konserven', '🐟', 'st'),
            (95, 'Bohnen', 'konserven', '🫘', 'st'),
            (96, 'Kondensmilch', 'konserven', '🫙', 'st'),
            (97, 'Pastete', 'konserven', '🫙', 'st')
        ]

        cursor.executemany(
            "INSERT INTO products (id, name, category, emoji, unit_type) VALUES (?, ?, ?, ?, ?)",
            items
        )
        conn.commit()

    conn.close()


def get_products_by_cat(category_code):
    """Fetches all products belonging to a specific category."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, emoji, unit_type FROM products WHERE category = ?", (category_code,))
    data = cursor.fetchall()
    conn.close()
    return data


def get_cart_items(user_id):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.name, p.emoji, c.quantity, c.is_bought, p.unit_type, p.category 
        FROM cart c 
        JOIN products p ON c.product_id = p.id 
        WHERE c.user_id = ? AND c.is_bought != -1
        ORDER BY p.category ASC, p.name ASC
    """, (user_id,))
    data = cursor.fetchall()
    conn.close()
    return data


def get_category_by_id(product_id):
    """Returns the category code for a specific product."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT category FROM products WHERE id = ?", (product_id,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else None


def toggle_bought_status(user_id, product_id):
    """Toggles the is_bought status between 0 and 1."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE cart SET is_bought = 1 - is_bought WHERE user_id = ? AND product_id = ?",
        (user_id, product_id)
    )
    conn.commit()
    conn.close()


def delete_from_cart(user_id, product_id):
    """Marks an item as deleted using status -1."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE cart SET is_bought = -1 WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    conn.commit()
    conn.close()


def save_to_history(user_id):
    """Moves ONLY purchased items to history and clears the user's cart."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO purchase_history (user_id, product_name, quantity, date)
        SELECT c.user_id, p.name, c.quantity, datetime('now')
        FROM cart c JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ? AND c.is_bought = 1
    """, (user_id,))

    cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))

    conn.commit()
    conn.close()


def clear_cart(user_id):
    """Wipes all items from the cart for a specific user."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


# -------------------------
# SMART SEARCH + CUSTOM ITEM
# -------------------------

def find_product_smart(user_input):
    """Performs fuzzy matching to find a product ID based on user text input."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM products")
    all_products = cursor.fetchall()
    conn.close()

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


def add_unknown_to_cart(user_id, item_name, quantity=1):
    """Creates a custom product if not found in DB and adds it to user cart."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM products WHERE name = ? AND category = 'other'", (item_name,))
    result = cursor.fetchone()

    if result:
        product_id = result[0]
    else:
        cursor.execute(
            "INSERT INTO products (name, category, emoji, unit_type) VALUES (?, ?, ?, ?)",
            (item_name, 'other', '📝', 'st')
        )
        product_id = cursor.lastrowid

    conn.commit()
    conn.close()

    add_to_cart_smart(user_id, product_id, quantity)


# -------------------------
# QUANTITY / STEPS (ONE PLACE)
# -------------------------

def get_product_meta(product_id: int):
    """Fetches unit type, category, and name for quantity calculations."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT unit_type, category, name FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None, None, None
    return row[0], row[1], row[2]


def calc_step(product_id: int, unit_type: str, category: str, mode: str) -> float:
    """
    Calculates the increment step based on product type and UI context.
    mode:
      - 'menu'  -> Initial add from category / Quick add default
      - 'edit'  -> Fine-tuning in the cart (+/- buttons)
    """
    unit_type = (unit_type or "").lower()
    category = (category or "").lower()

    # Special rule: Eggs are added as a pack of 10 by default
    if product_id == EGGS_ID and mode == "menu":
        return 10.0

    # Piece-based items (Stück) always use 1.0 step
    if unit_type in {"pcs", "st", "st.", "шт"}:
        return 1.0

    # Weight-based items (Kilograms)
    if unit_type == "kg":
        return 0.5 if mode == "menu" else 0.25

    # Liquids (Liters) or Drinks
    if unit_type in {"liter", "l"} or category == "drinks":
        return 1.0 if mode == "menu" else 0.5

    return 1.0


def add_to_cart_smart(user_id, product_id, quantity=1.0):
    """Adds a specific quantity to the cart or updates the existing entry."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    result = cursor.fetchone()

    if result:
        new_quantity = result[0] + float(quantity)
        cursor.execute(
            "UPDATE cart SET quantity = ? WHERE user_id = ? AND product_id = ?",
            (new_quantity, user_id, product_id)
        )
    else:
        cursor.execute(
            "INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)",
            (user_id, product_id, float(quantity))
        )

    conn.commit()
    conn.close()


def change_item_qty(user_id: int, product_id: int, is_plus: bool, mode: str):
    """
    Universal handler for changing item quantities:
    - If item doesn't exist: adds with appropriate step
    - If exists: increments/decrements by step
    - If result is <= 0: removes item from cart
    """
    unit_type, category, name = get_product_meta(product_id)
    if unit_type is None:
        return

    step = calc_step(product_id, unit_type, category, mode)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    row = cursor.fetchone()
    current_qty = row[0] if row else 0.0

    new_qty = round(current_qty + step, 2) if is_plus else round(current_qty - step, 2)

    if new_qty <= 0:
        cursor.execute("DELETE FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    else:
        if row:
            cursor.execute(
                "UPDATE cart SET quantity = ? WHERE user_id = ? AND product_id = ?",
                (new_qty, user_id, product_id)
            )
        else:
            cursor.execute(
                "INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)",
                (user_id, product_id, new_qty)
            )

    conn.commit()
    conn.close()


def update_item_qty(user_id, product_id, is_plus=True, is_menu_click=False):
    """Wrapper for backward compatibility with existing code calls."""
    mode = "menu" if is_menu_click else "edit"
    change_item_qty(user_id, product_id, is_plus=is_plus, mode=mode)