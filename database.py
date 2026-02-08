import sqlite3


def init_db():
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()

    # 1. Таблица всех товаров
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT, 
        category TEXT, 
        emoji TEXT,
        unit_type TEXT DEFAULT 'pc',
        price FLOAT DEFAULT 0.0
    )""")

    # 2. Таблица текущей корзины
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cart (
        user_id INTEGER, 
        product_id INTEGER, 
        quantity REAL DEFAULT 0,
        is_bought INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, product_id)
    )""")

    # 3. Таблица истории (статистика)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS purchase_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_name TEXT,
        quantity REAL,
        price FLOAT,
        date TEXT
    )""")

    # Наполнение товарами (выполняется если база пустая)
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        items = [
            # Овощи (veg)
            ('Kartoffel', 'veg', '🥔', 'kg'),
            ('Tomate', 'veg', '🍅', 'kg'),
            ('Gurke', 'veg', '🥒', 'pc'),
            ('Zwiebel', 'veg', '🧅', 'kg'),
            # Фрукты (fruits)
            ('Äpfel', 'fruits', '🍎', 'kg'),
            ('Banane', 'fruits', '🍌', 'kg'),
            ('Zitrone', 'fruits', '🍋', 'pc'),
            # Мясо (meat)
            ('Fleisch', 'meat', '🥩', 'kg'),
            ('Hähnchen', 'meat', '🍗', 'kg'),
            ('Wurst', 'meat', '🌭', 'pc'),
            # Молочка (dairy)
            ('Milch', 'dairy', '🥛', 'liter'),
            ('Eier', 'dairy', '🥚', 'pc'),
            ('Käse', 'dairy', '🧀', 'kg'),
            ('Joghurt', 'dairy', '🍦', 'pc'),
            # Напитки (drinks)
            ('Wasser', 'drinks', '💧', 'liter'),
            ('Cola', 'drinks', '🥤', 'liter'),
            ('Kaffee', 'drinks', '☕', 'pc'),
            # Остальное
            ('Brot', 'bakery', '🍞', 'pc'),
            ('Schoko', 'sweets', '🍫', 'pc'),
            ('Seife', 'hygiene', '🧼', 'pc'),
            ('T.Papier', 'hygiene', '🧻', 'pc')
        ]
        cursor.executemany(
            "INSERT INTO products (name, category, emoji, unit_type) VALUES (?, ?, ?, ?)",
            items
        )

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

    # Определяем шаг добавления
    cursor.execute("SELECT name, unit_type FROM products WHERE id = ?", (product_id,))
    res = cursor.fetchone()
    name, unit = res[0], res[1]

    if 'Eier' in name or name.lower() == 'яйца':
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
    # Важно: тянем unit_type через JOIN для правильного отображения в списке
    cursor.execute("""
    SELECT p.id, p.name, p.emoji, c.quantity, c.is_bought, p.unit_type 
    FROM cart c 
    JOIN products p ON c.product_id = p.id 
    WHERE c.user_id = ?""", (user_id,))
    data = cursor.fetchall()
    conn.close()
    return data

# Добавь это в database.py
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

    # Переносим только отмеченные галочкой
    cursor.execute("""
        INSERT INTO purchase_history (user_id, product_name, quantity, date)
        SELECT c.user_id, p.name, c.quantity, datetime('now')
        FROM cart c JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ? AND c.is_bought = 1
    """, (user_id,))

    # Удаляем абсолютно всё из корзины этого юзера
    cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))

    conn.commit()
    conn.close()

def clear_cart(user_id):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()