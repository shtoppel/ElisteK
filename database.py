import sqlite3


def init_db():
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()

    # 1. Table of all products
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT, 
        category TEXT, 
        emoji TEXT,
        unit_type TEXT DEFAULT 'pc',
        price FLOAT DEFAULT 0.0
    )""")

    # 2. Table of the current shopping cart
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cart (
        user_id INTEGER, 
        product_id INTEGER, 
        quantity REAL DEFAULT 0,
        is_bought INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, product_id)
    )""")

    # 3. Progress table (statistics)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS purchase_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_name TEXT,
        quantity REAL,
        price FLOAT,
        date TEXT
    )""")

    # Fill with goods (executed when the database is empty)
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
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
            (81, 'Duschgel', 'hygiene', '🚿', 'pcs'), (82, 'Deo', 'hygiene', '🌬️', 'pcs')
        ]
        cursor.execute("SELECT count(*) FROM products")
        if cursor.fetchone()[0] == 0:
            # There should be FIVE question marks here: (?, ?, ?, ?, ?)
            cursor.executemany(
                "INSERT INTO products (id, name, category, emoji, unit_type) VALUES (?, ?, ?, ?, ?)",
                items
            )
            conn.commit()

    conn.commit()
    conn.close()


def get_products_by_cat(category):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, emoji, unit_type FROM products WHERE category = ?", (category,))
    data = cursor.fetchall()
    conn.close()
    return data


def add_to_cart_smart(user_id, product_id):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()

    # We determine the step to add
    cursor.execute("SELECT name, unit_type FROM products WHERE id = ?", (product_id,))
    res = cursor.fetchone()
    name, unit = res[0], res[1]

    if 'Eier' in name or name.lower() == 'Eier':
        step = 10.0
    elif unit == 'kg':
        step = 0.5
    else:
        step = 1.0

    cursor.execute("""
    INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)
    ON CONFLICT(user_id, product_id) DO UPDATE SET quantity = quantity + ?
    """, (user_id, product_id, step, step))

    conn.commit()
    conn.close()


def get_cart_items(user_id):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    # Important: We pull unit_type via JOIN to display it correctly in the list.
    cursor.execute("""
    SELECT p.id, p.name, p.emoji, c.quantity, c.is_bought, p.unit_type 
    FROM cart c 
    JOIN products p ON c.product_id = p.id 
    WHERE c.user_id = ?""", (user_id,))
    data = cursor.fetchall()
    conn.close()
    return data

def get_category_by_id(product_id):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT category FROM products WHERE id = ?", (product_id,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else None

def toggle_bought_status(user_id, product_id):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE cart SET is_bought = 1 - is_bought WHERE user_id = ? AND product_id = ?",
                   (user_id, product_id))
    conn.commit()
    conn.close()


def delete_from_cart(user_id, product_id):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    conn.commit()
    conn.close()


def save_to_history(user_id):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()

    # Transfer only items marked with a check mark
    cursor.execute("""
        INSERT INTO purchase_history (user_id, product_name, quantity, date)
        SELECT c.user_id, p.name, c.quantity, datetime('now')
        FROM cart c JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ? AND c.is_bought = 1
    """, (user_id,))

    # We delete absolutely everything from this user's cart.
    cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))

    conn.commit()
    conn.close()

def clear_cart(user_id):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()