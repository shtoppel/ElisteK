import sqlite3
from thefuzz import process, fuzz

DB_NAME = 'shop.db'

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

    # Check if products exist, if not, insert initial data
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        # Use simple category names: 'veg', 'fruits', etc.
        items = [
            # GEMÜSE 🥦
            (1, 'Kartoffeln', 'veg', '🥔', 'kg'), (2, 'Tomaten', 'veg', '🍅', 'kg'),
            (3, 'Gurken', 'veg', '🥒', 'pcs'), (4, 'Zwiebeln', 'veg', '🧅', 'kg'),
            (5, 'Karotten', 'veg', '🥕', 'kg'), (6, 'Paprika', 'veg', '👝', 'kg'),
            (7, 'Knoblauch', 'veg', '🧄', 'pcs'), (8, 'Brokkoli', 'veg', '🥦', 'pcs'),
            (9, 'Blumenkohl', 'veg', '🥦', 'pcs'), (10, 'Salat', 'veg', '🥬', 'pcs'),
            (11, 'Zucchini', 'veg', '🥒', 'kg'), (12, 'Aubergine', 'veg', '🍆', 'pcs'),
            (13, 'Pilze', 'veg', '🍄', 'kg'), (14, 'Ingwer', 'veg', '🫚', 'kg'),
            (15, 'Avocado', 'veg', '🥑', 'pcs'), (16, 'Spinat', 'veg', '🍃', 'pcs'),

            # OBST 🍎
            (17, 'Äpfel', 'fruits', '🍎', 'kg'), (18, 'Bananen', 'fruits', '🍌', 'kg'),
            (19, 'Orangen', 'fruits', '🍊', 'kg'), (20, 'Zitronen', 'fruits', '🍋', 'pcs'),
            (21, 'Weintrauben', 'fruits', '🍇', 'kg'), (22, 'Erdbeeren', 'fruits', '🍓', 'pcs'),
            (23, 'Blaubeeren', 'fruits', '🫐', 'pcs'), (24, 'Himbeeren', 'fruits', '🍒', 'pcs'),
            (25, 'Birnen', 'fruits', '🍐', 'kg'), (26, 'Pfirsiche', 'fruits', '🍑', 'kg'),
            (27, 'Kiwi', 'fruits', '🥝', 'pcs'), (28, 'Ananas', 'fruits', '🍍', 'pcs'),
            (29, 'Melone', 'fruits', '🍉', 'pcs'), (30, 'Mango', 'fruits', '🥭', 'pcs'),

            # FLEISCH & WURST 🥩
            (31, 'Hähnchenbrust', 'meat', '🍗', 'kg'), (32, 'Rindfleisch', 'meat', '🥩', 'kg'),
            (33, 'Schweinefleisch', 'meat', '🍖', 'kg'), (34, 'Hackfleisch', 'meat', '🥘', 'kg'),
            (35, 'Schinken', 'meat', '🥓', 'kg'), (36, 'Salami', 'meat', '🍕', 'pcs'),
            (37, 'Würstchen', 'meat', '🌭', 'pcs'), (38, 'Putenfleisch', 'meat', '🦃', 'kg'),
            (39, 'Lachs', 'meat', '🐟', 'kg'), (40, 'Garnelen', 'meat', '🍤', 'kg'),

            # BACKWAREN 🥐
            (41, 'Weißbrot', 'bakery', '🍞', 'pcs'), (42, 'Baguette', 'bakery', '🥖', 'pcs'),
            (43, 'Brötchen', 'bakery', '🥐', 'pcs'), (44, 'Toastbrot', 'bakery', '🥪', 'pcs'),
            (45, 'Vollkornbrot', 'bakery', '🍞', 'pcs'), (46, 'Brezel', 'bakery', '🥨', 'pcs'),
            (47, 'Croissant', 'bakery', '🥐', 'pcs'), (48, 'Kuchen', 'bakery', '🍰', 'pcs'),

            # MILCHPRODUKTE 🥛
            (49, 'Milch', 'dairy', '🥛', 'liter'), (50, 'Quark', 'dairy', '⚪', 'pcs'),
            (51, 'Käse', 'dairy', '🧀', 'kg'), (52, 'Sahne', 'dairy', '🍶', 'pcs'),
            (53, 'Butter', 'dairy', '🧈', 'pcs'), (54, 'Eier', 'dairy', '🥚', 'pcs'),
            (55, 'Joghurt', 'dairy', '🍦', 'pcs'), (56, 'Frischkäse', 'dairy', '🥣', 'pcs'),
            (57, 'Schmand', 'dairy', '🥛', 'pcs'), (58, 'Kefir', 'dairy', '🥤', 'liter'),

            # GETRÄNKE 🥤
            (59, 'Mineralwasser', 'drinks', '💧', 'pcs'), (60, 'Saft', 'drinks', '🧃', 'liter'),
            (61, 'Cola', 'drinks', '🥤', 'liter'), (62, 'Bier', 'drinks', '🍺', 'liter'),
            (63, 'Kaffee', 'drinks', '☕', 'pcs'), (64, 'Tee', 'drinks', '🫖', 'pcs'),
            (65, 'Wein', 'drinks', '🍷', 'liter'), (66, 'Eistee', 'drinks', '🍹', 'liter'),

            # SÜSSIGKEITEN 🍫
            (67, 'Schokolade', 'sweets', '🍫', 'pcs'), (68, 'Kekse', 'sweets', '🍪', 'kg'),
            (69, 'Gummibärchen', 'sweets', '🍬', 'pcs'), (70, 'Eiscreme', 'sweets', '🍦', 'pcs'),
            (71, 'Chips', 'sweets', '🥔', 'pcs'), (72, 'Nüsse', 'sweets', '🥜', 'kg'),
            (73, 'Honig', 'sweets', '🍯', 'pcs'), (74, 'Marmelade', 'sweets', '🍓', 'pcs'),

            # HYGIENE 🧼
            (75, 'Seife', 'hygiene', '🧼', 'pcs'), (76, 'Shampoo', 'hygiene', '🧴', 'pcs'),
            (77, 'Zahnpasta', 'hygiene', '🪥', 'pcs'), (78, 'Toilettenpapier', 'hygiene', '🧻', 'pcs'),
            (79, 'Waschmittel', 'hygiene', '🧺', 'pcs'), (80, 'Küchenrollen', 'hygiene', '🧻', 'pcs'),
            (81, 'Duschgel', 'hygiene', '🚿', 'pcs'), (82, 'Deo', 'hygiene', '🌬️', 'pcs'),

            # Tiefkühlkost
            (83, 'Pelmeni', 'tiefkühlkost', '🥟', 'kg'), (84, 'Pizza', 'tiefkühlkost', '🍕', 'st'),
            (85, 'Pommes', 'tiefkühlkost', '🍟', 'kg'),  (86, 'Nuggets', 'tiefkühlkost', '🥡', 'kg'),
            (87, 'Burger', 'tiefkühlkost', '🍔', 'st'),

            # Konserven
            (88, 'Thunfisch', 'konserven', '🫙', 'st'),
            (89, 'Dose Erbsen', 'konserven', '🫛', 'st'),
            (90, 'Dosenmais', 'konserven', '🌽', 'st'),
            (91, 'Gewürzgurken', 'konserven', '🥒', 'st'),  # Была ошибка тут
            (92, 'Konservierte Tomaten', 'konserven', '🥫', 'st'),
            (93, 'Oliven', 'konserven', '🫒', 'st'),
            (94, 'Sprotten', 'konserven', '🐟', 'st'),  # Добавил рыбку 🐟
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
    # Add p.category to SELECT and sorting at the end
    cursor.execute("""
        SELECT p.id, p.name, p.emoji, c.quantity, c.is_bought, p.unit_type, p.category 
        FROM cart c 
        JOIN products p ON c.product_id = p.id 
        WHERE c.user_id = ?
        ORDER BY p.category ASC, p.name ASC
    """, (user_id,))
    data = cursor.fetchall()
    conn.close()
    return data


def add_to_cart_smart(user_id, product_id, quantity=1.0): # Используем 1.0 по умолчанию
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Checking the current quantity
    cursor.execute("SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    result = cursor.fetchone()

    if result:
        # We add (for example, 0.5 + 0.5 becomes 1.0)
        new_quantity = result[0] + float(quantity)
        cursor.execute("UPDATE cart SET quantity = ? WHERE user_id = ? AND product_id = ?",
                       (new_quantity, user_id, product_id))
    else:
        cursor.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)",
                       (user_id, product_id, float(quantity)))
    conn.commit()
    conn.close()

def get_category_by_id(product_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT category FROM products WHERE id = ?", (product_id,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else None

def toggle_bought_status(user_id, product_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE cart SET is_bought = 1 - is_bought WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    conn.commit()
    conn.close()

def delete_from_cart(user_id, product_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Instead of DELETE, we do UPDATE. Status -1 will mean “removed from the list.”
    cursor.execute("UPDATE cart SET is_bought = -1 WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    conn.commit()
    conn.close()

def save_to_history(user_id):
    """Moves bought items to history and clears the cart."""
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
    """
    Completely removes all items from a specific user's cart.
    Used for the 'Clear List' functionality.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def find_product_smart(user_input):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()

    # We receive all goods from the warehouse
    cursor.execute("SELECT id, name FROM products")
    all_products = cursor.fetchall()  # Список кортежей [(1, 'Яблоки'), (2, 'Хлеб')]
    conn.close()

    #1. Trying to find an exact match
    for p_id, p_name in all_products:
        if p_name.lower() == user_input.lower():
            return p_id

    #2. If you can't find it, look for something similar (80% match threshold).
    names = [p[1] for p in all_products]
    best_match, score = process.extractOne(user_input, names, scorer=fuzz.WRatio)

    if score > 80:
        # Find the ID of this best match
        for p_id, p_name in all_products:
            if p_name == best_match:
                return p_id

    return None


def add_unknown_to_cart(user_id, item_name, quantity=1):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()

    # Check if such a “custom” product already exists.
    # Use the category ‘other’ (make sure it is a string, not the number 999).
    cursor.execute("SELECT id FROM products WHERE name = ? AND category = 'other'", (item_name,))
    result = cursor.fetchone()

    if result:
        product_id = result[0]
    else:
        # Add a new product. Columns: name, category, emoji, unit_type
        cursor.execute(
            "INSERT INTO products (name, category, emoji, unit_type) VALUES (?, ?, ?, ?)",
            (item_name, 'other', '📝', 'st')
        )
        product_id = cursor.lastrowid

    conn.commit()
    conn.close()

    # Add to cart
    add_to_cart_smart(user_id, product_id, quantity)