from telebot import types


def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    cats = [
        ('Овощи 🥦', 'cat_veg'), ('Фрукты 🍎', 'cat_fruits'),
        ('Мясо 🥩', 'cat_meat'), ('Выпечка 🥐', 'cat_bakery'),
        ('Молочка 🥛', 'cat_dairy'), ('Напитки 🥤', 'cat_drinks'),
        ('Сладости 🍫', 'cat_sweets'), ('Гигиена 🧼', 'cat_hygiene')
    ]
    markup.add(*[types.InlineKeyboardButton(text=c[0], callback_data=c[1]) for c in cats])

    # Кнопки управления
    markup.row(types.InlineKeyboardButton(text="🛒 Показать список", callback_data="show_cart"))
    markup.row(
        types.InlineKeyboardButton(text="🧹 Очистить", callback_data="clear_confirm"),
        types.InlineKeyboardButton(text="✅ Завершить", callback_data="finish_list")
    )
    return markup


def products_menu(products_list, user_cart):
    markup = types.InlineKeyboardMarkup(row_width=1)  # В один ряд удобнее с длинными названиями
    cart_data = {item[0]: (item[3], item[4]) for item in user_cart}  # id: (qty, status)

    for p_id, name, emoji, unit in products_list:
        text = f"{emoji} {name}"
        if p_id in cart_data:
            qty, status = cart_data[p_id]
            unit_name = "кг" if unit == "kg" else "л" if unit == "liter" else "шт"
            # Форматируем число: если целое — без точки, если 0.5 — с точкой
            display_qty = int(qty) if qty % 1 == 0 else qty
            text = f"✅ {text} ({display_qty} {unit_name})"

        markup.add(types.InlineKeyboardButton(text=text, callback_data=f"add_{p_id}"))

    markup.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    return markup


def final_cart_menu(cart_items):
    markup = types.InlineKeyboardMarkup()
    # ВАЖНО: Тут должно быть 6 переменных!
    for p_id, name, emoji, qty, status, unit in cart_items:
        unit_name = "кг" if unit == "kg" else "л" if unit == "liter" else "шт"
        display_qty = int(qty) if qty % 1 == 0 else qty

        check = "✅" if status else "▫️"
        # Если куплено — можно добавить визуальное зачеркивание (опционально)
        btn_text = f"{check} {emoji} {name}: {display_qty} {unit_name}"

        # Кнопка переключения статуса и кнопка удаления
        markup.row(
            types.InlineKeyboardButton(text=btn_text, callback_data=f"toggle_{p_id}"),
            types.InlineKeyboardButton(text="❌", callback_data=f"del_{p_id}")
        )

    markup.row(types.InlineKeyboardButton(text="➕ Добавить ещё", callback_data="back_to_main"))
    markup.row(types.InlineKeyboardButton(text="🏁 ЗАВЕРШИТЬ ПОКУПКУ", callback_data="complete_shopping"))
    return markup

def start_new_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="➕ Создать новый список", callback_data="back_to_main"))
    return markup