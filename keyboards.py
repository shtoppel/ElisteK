from telebot import types


def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    cats = [
        ('Gemüse 🥦', 'cat_veg'), ('Obst 🍎', 'cat_fruits'),
        ('Fleisch 🥩', 'cat_meat'), ('Backwaren 🥐', 'cat_bakery'),
        ('Milchprodukte 🥛', 'cat_dairy'), ('Getränke 🥤', 'cat_drinks'),
        ('Süßigkeiten 🍫', 'cat_sweets'), ('Hygiene 🧼', 'cat_hygiene')
    ]
    markup.add(*[types.InlineKeyboardButton(text=c[0], callback_data=c[1]) for c in cats])

    # Control buttons
    markup.row(types.InlineKeyboardButton(text="🛒 Liste anzeigen", callback_data="show_cart"))
    markup.row(
        types.InlineKeyboardButton(text="🧹 Löschen", callback_data="clear_confirm"),
        types.InlineKeyboardButton(text="✅ Beenden", callback_data="finish_list")
    )
    return markup


def products_menu(products_list, user_cart):
    markup = types.InlineKeyboardMarkup(row_width=1)  # В один ряд удобнее с длинными названиями
    cart_data = {item[0]: (item[3], item[4]) for item in user_cart}  # id: (qty, status)

    for p_id, name, emoji, unit in products_list:
        text = f"{emoji} {name}"
        if p_id in cart_data:
            qty, status = cart_data[p_id]
            unit_name = "kg" if unit == "kg" else "l" if unit == "liter" else "st"
            # Форматируем число: если целое — без точки, если 0.5 — с точкой
            display_qty = int(qty) if qty % 1 == 0 else qty
            text = f"✅ {text} ({display_qty} {unit_name})"

        markup.add(types.InlineKeyboardButton(text=text, callback_data=f"add_{p_id}"))

    markup.add(types.InlineKeyboardButton(text="⬅️ Zu den Kategorien", callback_data="back_to_main"))
    return markup


def final_cart_menu(cart_items):
    markup = types.InlineKeyboardMarkup()
    # 1. Drawing products
    for p_id, name, emoji, qty, status, unit in cart_items:
        unit_name = "kg" if unit == "kg" else "l" if unit == "liter" else "st"
        display_qty = int(qty) if qty % 1 == 0 else qty
        check = "✅" if status else "▫️"
        btn_text = f"{check} {emoji} {name}: {display_qty} {unit_name}"

        markup.row(
            types.InlineKeyboardButton(text=btn_text, callback_data=f"toggle_{p_id}"),
            types.InlineKeyboardButton(text="❌", callback_data=f"del_{p_id}")
        )

    # 2. ADD A SUBMIT BUTTON HERE!
    markup.row(types.InlineKeyboardButton(
        text="🚀 LISTE SENDEN",
        switch_inline_query="share"  # This calls the inline mode.
    ))

    # 3. Other control buttons
    markup.row(types.InlineKeyboardButton(text="➕ Zu den Kategorien", callback_data="back_to_main"))
    markup.row(types.InlineKeyboardButton(text="🏁 KAUF ABSCHLIESSEN", callback_data="complete_shopping"))
    return markup

def start_new_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="➕ Neue Liste erstellen", callback_data="back_to_main"))
    return markup


def cart_menu(cart_items):
    markup = types.InlineKeyboardMarkup(row_width=2)

    # First, we draw the list (as I did).
    for item in cart_items:
        # Let's assume that item[0] is the ID and item[1] is the name.
        markup.add(types.InlineKeyboardButton(f"❌ {item[1]}", callback_data=f"del_{item[0]}"))

    # Forward button
    # switch_inline_query_current_chat="" opens the search in the current chat
    # switch_inline_query="" opens the contact selection
    markup.row(types.InlineKeyboardButton(
        text="🚀 Liste an Kontakt senden",
        switch_inline_query="share"  # Key-word
    ))

    markup.row(types.InlineKeyboardButton("⬅️ Zu den Kategorien", callback_data="back_to_main"))
    return markup


def shared_cart_menu(cart_items, owner_id):
    markup = types.InlineKeyboardMarkup()
    for p_id, name, emoji, qty, status, unit in cart_items:
        unit_name = "kg" if unit == "kg" else "l" if unit == "liter" else "st"
        display_qty = int(qty) if qty % 1 == 0 else qty
        check = "✅" if status else "▫️"

        # In callback_data, we add owner_id so that the bot knows whose shopping cart to modify.
        markup.row(
            types.InlineKeyboardButton(
                text=f"{check} {emoji} {name}: {display_qty} {unit_name}",
                callback_data=f"toggle_{p_id}_{owner_id}"
            ),
            # If you want your partner to be able to delete messages too:
            types.InlineKeyboardButton(text="❌", callback_data=f"del_{p_id}_{owner_id}")
        )

    markup.row(types.InlineKeyboardButton(text="🏁 ABSCHLIESSEN (BERICHT)", callback_data=f"finish_shared_{owner_id}"))
    return markup