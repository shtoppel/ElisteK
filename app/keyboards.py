from telebot import types


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
        types.InlineKeyboardButton(text="🧹 Alles Löschen", callback_data="clear_confirm"),
        types.InlineKeyboardButton(text="✅ Beenden", callback_data="finish_list")
    )
    return markup


def products_menu(products_list, user_cart):
    markup = types.InlineKeyboardMarkup(row_width=2)
    cart_data = {item[0]: item[3] for item in user_cart}

    for p_id, name, emoji, unit in products_list:
        text = f"{emoji} {name}"
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


def final_cart_menu(cart_items, edit_mode=False, delete_mode=False, selected=None, confirm_delete=False):
    selected = selected or set()
    markup = types.InlineKeyboardMarkup()
    cat_names = {
        'veg': '🥦 GEMÜSE', 'fruits': '🍎 OBST', 'meat': '🥩 FLEISCH',
        'bakery': '🥐 BACKWAREN', 'dairy': '🥛 MILCHPRODUKTE', 'drinks': '🥤 GETRÄNKE',
        'sweets': '🍫 SÜSSIGKEITEN', 'tiefkühlkost': '❄️ TK', 'konserven': '🥫 DOSEN',
        'hygiene': '🧼 HYGIENE', 'other': '📝 ANDERES'
    }

    active_items = [item for item in cart_items if item[4] != -1]

    # Header for delete mode
    if delete_mode and not edit_mode:
        markup.row(types.InlineKeyboardButton(text="🗑️ LÖSCHMODUS:", callback_data="none"))
        markup.row(types.InlineKeyboardButton(text="Wähle Artikel zum Löschen aus:", callback_data="none"))

    if not edit_mode:
        grouped = {}
        for item in active_items:
            cat = item[6]
            grouped.setdefault(cat, []).append(item)

        for cat_code, header in cat_names.items():
            if cat_code not in grouped:
                continue

            markup.row(types.InlineKeyboardButton(text=f"── {header} ──", callback_data="none"))

            row_btns = []
            for item in grouped[cat_code]:
                p_id, name, emoji, qty, status, unit_type, _ = item
                display_qty = int(qty) if qty % 1 == 0 else qty
                u_label = "kg" if unit_type == "kg" else "l" if unit_type == "liter" else "st"

                if delete_mode:
                    mark = "❌️" if p_id in selected else "▫️"
                    btn_text = f"{mark} {emoji}{name[:10]} {display_qty}{u_label}"
                    cb = f"sel_del_{p_id}"
                else:
                    check = "✅" if status == 1 else "▫️"
                    btn_text = f"{check} {emoji}{name[:10]} {display_qty}{u_label}"
                    cb = f"toggle_{p_id}"

                row_btns.append(types.InlineKeyboardButton(text=btn_text, callback_data=cb))

            for i in range(0, len(row_btns), 2):
                if i + 1 < len(row_btns):
                    markup.row(row_btns[i], row_btns[i + 1])
                else:
                    markup.row(row_btns[i])

        if delete_mode:
            n = len(selected)
            if confirm_delete:
                markup.row(
                    types.InlineKeyboardButton(text=f"✅ Ja, löschen ({n})", callback_data="del_confirm_yes"),
                    types.InlineKeyboardButton(text="↩️ Nein", callback_data="del_confirm_no"),
                )
            else:
                markup.row(types.InlineKeyboardButton(text=f"🧹 Löschen ({n})", callback_data="del_selected"))

            markup.row(types.InlineKeyboardButton(text="↩️ Abbrechen", callback_data="del_cancel"))

        else:
            markup.row(types.InlineKeyboardButton(text="🗑️ Entfernen (Auswahl)", callback_data="del_mode"))

            if any(item[4] == 1 for item in active_items):
                markup.row(types.InlineKeyboardButton(
                    text="✏️ Mengen ändern (für markierte Waren)",
                    callback_data="mode_edit"
                ))

            markup.row(types.InlineKeyboardButton(text="🚀 LISTE SENDEN", switch_inline_query="share"))

            markup.row(
                types.InlineKeyboardButton(text="➕ Kategorien", callback_data="back_to_main"),
                types.InlineKeyboardButton(text="🏁 ABSCHLIESSEN", callback_data="complete_shopping")
            )

    else:
        markup.row(types.InlineKeyboardButton(text="⚙️ MENGEN ANPASSEN:", callback_data="none"))
        checked_items = [item for item in active_items if item[4] == 1]

        for item in checked_items[:20]:
            p_id, name, emoji, qty, status, unit_type, _ = item
            display_qty = int(qty) if qty % 1 == 0 else qty
            u_label = "kg" if unit_type == "kg" else "l" if unit_type == "liter" else "st"

            markup.row(types.InlineKeyboardButton(text=f"{emoji} {name}", callback_data="none"))
            markup.row(
                types.InlineKeyboardButton(text="  ➖  ", callback_data=f"minus_{p_id}"),
                types.InlineKeyboardButton(text=f"{display_qty} {u_label}", callback_data="none"),
                types.InlineKeyboardButton(text="  ➕  ", callback_data=f"plus_{p_id}")
            )

        if len(checked_items) > 20:
            markup.row(types.InlineKeyboardButton(text="⚠️ Weitere Artikel im Hauptmenü", callback_data="none"))

        markup.row(types.InlineKeyboardButton(text="✅ Fertig/Zurück", callback_data="mode_view"))

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
        'tiefkühlkost': '❄️ TK', 'konserven': '🥫 DOSEN',
        'hygiene': '🧼 HYGIENE', 'other': '📝 ANDERES'
    }

    active_items = [item for item in cart_items if item[3] > 0 and item[4] != -1]

    grouped = {}
    for item in active_items:
        cat = item[6]
        grouped.setdefault(cat, []).append(item)

    for cat_code, header in cat_names.items():
        if cat_code not in grouped:
            continue

        markup.row(types.InlineKeyboardButton(text=f"── {header} ──", callback_data="none"))

        row_btns = []
        for item in grouped[cat_code]:
            p_id, name, emoji, qty, status, unit, _ = item
            unit_name = "kg" if unit == "kg" else "l" if unit == "liter" else "st"
            display_qty = int(qty) if qty % 1 == 0 else qty
            check = "✅" if status == 1 else "▫️"
            btn_text = f"{check} {emoji}{name[:9]} {display_qty}{unit_name}"

            row_btns.append(types.InlineKeyboardButton(
                text=btn_text,
                callback_data=f"toggle_{p_id}_{owner_id}"
            ))

        for i in range(0, len(row_btns), 2):
            if i + 1 < len(row_btns):
                markup.row(row_btns[i], row_btns[i + 1])
            else:
                markup.row(row_btns[i])

    markup.row(types.InlineKeyboardButton(text="🏁 KAUF ABSCHLIESSEN", callback_data=f"finish_shared_{owner_id}"))
    return markup