import os
import sqlite3

DB_PATH = os.getenv("DB_PATH", "shop.db")

def connect() -> sqlite3.Connection:
    # timeout помогает при частых кликах
    conn = sqlite3.connect(DB_PATH, timeout=5)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

def init_db():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT, 
        category TEXT, 
        emoji TEXT,
        unit_type TEXT DEFAULT 'pcs',
        price FLOAT DEFAULT 0.0
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cart (
        user_id INTEGER, 
        product_id INTEGER, 
        quantity REAL DEFAULT 0,
        is_bought INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, product_id)
    )""")

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