from telebot import types


# Fixed: Added 'count' argument to match the call in main.py
def main_menu(count=0):
    markup = types.InlineKeyboardMarkup(row_width=2)
    cats = [
        ('Gemüse 🥦', 'cat_veg'), ('Obst 🍎', 'cat_fruits'),
        ('Fleisch 🥩', 'cat_meat'), ('Backwaren 🥐', 'cat_bakery'),
        ('Milchprodukte 🥛', 'cat_dairy'), ('Getränke 🥤', 'cat_drinks'),
        ('Süßigkeiten 🍫', 'cat_sweets'), ('Tiefkühlkost ❄️', 'cat_tiefkühlkost'),
        ('Konserven 🥫', 'cat_konserven'),
        ('Hygiene 🧼', 'cat_hygiene')
    ]
    markup.add(*[types.InlineKeyboardButton(text=c[0], callback_data=c[1]) for c in cats])

    cart_btn_text = f"🛒 Warenkorb ({count})" if count > 0 else "🛒 Warenkorb (0)"
    markup.row(types.InlineKeyboardButton(text=cart_btn_text, callback_data="show_cart"))
    markup.row(
        types.InlineKeyboardButton(text="🧹 Löschen", callback_data="clear_confirm"),
        types.InlineKeyboardButton(text="✅ Beenden", callback_data="finish_list")
    )
    return markup

def products_menu(products_list, user_cart):
    markup = types.InlineKeyboardMarkup(row_width=2)
    # Create a dictionary for quick lookup: {product_id: quantity}
    cart_data = {item[0]: item[3] for item in user_cart}

    for p_id, name, emoji, unit in products_list:
        text = f"{emoji} {name}"
        # If product is in cart, add a checkmark and quantity
        if p_id in cart_data:
            qty = cart_data[p_id]
            unit_name = "kg" if unit == "kg" else "l" if unit == "liter" else "st"
            display_qty = int(qty) if qty % 1 == 0 else qty
            text = f"✅ {text} ({display_qty} {unit_name})"

        markup.add(types.InlineKeyboardButton(text=text, callback_data=f"add_{p_id}"))

    cart_count = len(user_cart)
    cart_text = f"🛒 Warenkorb ({cart_count})" if cart_count > 0 else "🛒 Warenkorb"
    markup.row(types.InlineKeyboardButton(text=cart_text, callback_data="show_cart"))
    markup.add(types.InlineKeyboardButton(text="⬅️ Zu den Kategorien", callback_data="back_to_main"))
    return markup


def final_cart_menu(cart_items):
    markup = types.InlineKeyboardMarkup()

    # Dictionary for beautiful headline titles
    cat_names = {
        'veg': '🥦 GEMÜSE',
        'fruits': '🍎 OBST',
        'meat': '🥩 FLEISCH',
        'bakery': '🥐 BACKWAREN',
        'dairy': '🥛 MILCHPRODUKTE',
        'drinks': '🥤 GETRÄNKE',
        'sweets': '🍫 SÜSSIGKEITEN',
        'tiefkühlkost': '❄️ TIEFKÜHLKOST',
        'konserven': '🥫 KONSERVEN',
        'hygiene': '🧼 HYGIENE'
    }

    current_cat = None

    for item in cart_items:
        p_id, name, emoji, qty, status, unit, category = item

        # If the status is -1 (deleted), we simply skip this item without drawing the button.
        if status == -1:
            continue

        # If the category has changed, add a separator.
        if category != current_cat:
            current_cat = category
            header_text = cat_names.get(category, "📦 ANDERES")
            # Button header (callback_data=“none” so that nothing happens when clicked)
            markup.row(types.InlineKeyboardButton(text=f"--- {header_text} ---", callback_data="none"))

        # Logic of rendering the product itself
        unit_name = "kg" if unit == "kg" else "l" if unit == "liter" else "st"
        display_qty = int(qty) if qty % 1 == 0 else qty
        check = "✅" if status else "▫️"
        btn_text = f"{check} {emoji} {name}: {display_qty} {unit_name}"

        markup.row(
            types.InlineKeyboardButton(text=btn_text, callback_data=f"toggle_{p_id}"),
            types.InlineKeyboardButton(text="❌", callback_data=f"del_{p_id}")
        )

    # Control buttons
    markup.row(types.InlineKeyboardButton(text="🚀 LISTE SENDEN", switch_inline_query="share"))
    markup.row(types.InlineKeyboardButton(text="➕ Zu den Kategorien", callback_data="back_to_main"))
    markup.row(types.InlineKeyboardButton(text="🏁 KAUF ABSCHLIESSEN", callback_data="complete_shopping"))
    return markup


def start_new_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="➕ Neue Liste erstellen", callback_data="back_to_main"))
    return markup


def shared_cart_menu(cart_items, owner_id):
    markup = types.InlineKeyboardMarkup()

    cat_names = {
        'veg': '🥦 GEMÜSE', 'fruits': '🍎 OBST', 'meat': '🥩 FLEISCH',
        'bakery': '🥐 BACKWAREN', 'dairy': '🥛 MILCHPRODUKTE',
        'drinks': '🥤 GETRÄNKE', 'sweets': '🍫 SÜSSIGKEITEN',
        'tiefkühlkost': '❄️ TIEFKÜHLKOST', 'konserven': '🥫 KONSERVEN',
        'hygiene': '🧼 HYGIENE',
    }

    current_cat = None

    for item in cart_items:
        p_id, name, emoji, qty, status, unit, category = item

        # If the status is -1 (deleted), we simply skip this item without drawing the button.
        if status == -1:
            continue

        # Add header if category changes
        if category != current_cat:
            current_cat = category
            header_text = cat_names.get(category, "📦 ANDERES")
            markup.row(types.InlineKeyboardButton(text=f"--- {header_text} ---", callback_data="none"))

        unit_name = "kg" if unit == "kg" else "l" if unit == "liter" else "st"
        display_qty = int(qty) if qty % 1 == 0 else qty
        check = "✅" if status else "▫️"

        # Partner buttons with owner_id
        markup.row(
            types.InlineKeyboardButton(
                text=f"{check} {emoji} {name}: {display_qty} {unit_name}",
                callback_data=f"toggle_{p_id}_{owner_id}"
            ),
            types.InlineKeyboardButton(text="❌", callback_data=f"del_{p_id}_{owner_id}")
        )

    markup.row(types.InlineKeyboardButton(text="🏁 ABSCHLIESSEN (BERICHT)", callback_data=f"finish_shared_{owner_id}"))
    return markup