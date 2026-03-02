import telebot
from telebot import types
from dotenv import load_dotenv
import os
import re

from app.db.schema import init_db
from app.db import repo
from app.services import cart_service, product_service
import app.keyboards as kb

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

last_list_msg = {}
delete_selection = {}  # user_id -> set(product_ids)


@bot.message_handler(commands=['start'])
def start(message):
    init_db()
    cart = repo.get_cart_items(message.from_user.id)
    bot.send_message(
        message.chat.id,
        f"Hallo {message.from_user.first_name}!👋 \nWählen Sie eine Kategorie 🤖:",
        reply_markup=kb.main_menu(len(cart))
    )


@bot.message_handler(commands=['info', 'help'])
def send_instructions(message):
    instructions = (
        "📖 *Bedienungsanleitung für deinen Einkaufshelfer*\n\n"
        "🛒 *1. Produkte hinzufügen:*\n"
        "• Nutze das **Menü**, um Kategorien und Produkte direkt auszuwählen.\n"
        "• Nutze den **Schnell-Modus** mit `#` für maximale Geschwindigkeit.\n\n"
        "⚡ *Schnell-Modus (#):*\n"
        "Schreibe eine Nachricht, die mit `#` beginnt. Mengen werden automatisch erkannt.\n"
        "🔹 *Wichtig:* Wird **keine Menge** angegeben, fügt der Bot automatisch **eine Standardmenge** hinzu.\n\n"
        "🔹 *Beispiele:*\n"
        "• `#Milch` — fügt automatisch die Standardmenge hinzu.\n"
        "• `#Tomaten 0.5` — fügt 0.5 kg hinzu.\n"
        "• `#Brot 2, Käse, Salami` — mehrere Artikel.\n\n"
        "🛍 *2. Warenkorb & Verwaltung:*\n"
        "• **Abhaken:** Tippe auf ein Produkt, um es als erledigt ✅ zu markieren.\n"
        "• **Mengen anpassen:** Klicke auf `✏️ Mengen ändern (für markierte Waren)`.\n"
        "  Dort kannst du с **(+)** und **(-)** die Menge präzise korrigieren.\n"
        "• **❌Löschen:** Nutze `🗑️ Entfernen (Auswahl)` (mit Bestätigung).\n\n"
        "🏁 *3. Einkauf abschließen:*\n"
        "• Wenn du fertig bist, markiere alle gekauften Artikel (✅) und drücke `🏁 ABSCHLIESSEN`.\n"
        "• **Teilen:** Mit `🚀 LISTE SENDEN` kannst du die Liste an deinen Partner/in schicken.\n\n"
        "💡 *Tipp:* Falls ein Produkt nicht im System ist, erscheint eine Taste, um es sofort neu zu erstellen!\n"
        "Enjoy your shopping! 🤖\n"
    )
    bot.send_message(message.chat.id, instructions, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):

    try:
        bot.answer_callback_query(call.id)
    except Exception:
        pass

    if call.data == "none":
        return

    user_id = call.from_user.id
    msg_id = call.message.message_id if call.message else None


    # 1) Category selected
    if call.data.startswith('cat_'):
        category = call.data.replace('cat_', '')
        products = repo.get_products_by_cat(category)
        cart = repo.get_cart_items(user_id)
        bot.edit_message_text(
            "Wählen Sie Produkte aus:", user_id, msg_id,
            reply_markup=kb.products_menu(products, cart)
        )

    elif call.data == "back_to_main":
        cart = repo.get_cart_items(user_id)
        bot.edit_message_text("Hauptmenü 📱:", user_id, msg_id, reply_markup=kb.main_menu(len(cart)))

    # 2) ADD product (unified step logic, eggs default 10)
    elif call.data.startswith('add_'):
        p_id = int(call.data.split('_')[1])
        cart_service.change_item_qty(user_id, p_id, is_plus=True, mode="menu")

        category = repo.get_category_by_id(p_id)
        products = repo.get_products_by_cat(category) if category else []
        cart = repo.get_cart_items(user_id)

        bot.edit_message_reply_markup(
            chat_id=user_id,
            message_id=msg_id,
            reply_markup=kb.products_menu(products, cart)
        )
        bot.answer_callback_query(call.id)

    # 3) Show cart
    elif call.data == "show_cart":
        cart = repo.get_cart_items(user_id)
        if not cart:
            bot.answer_callback_query(call.id, "Die Liste ist leer!", show_alert=True)
        else:
            delete_selection[user_id] = set()
            bot.edit_message_text(
                "Ihre aktuelle Einkaufsliste 🛒:",
                user_id, msg_id,
                reply_markup=kb.final_cart_menu(cart)
            )

    # 4) Clear
    elif call.data == "clear_confirm":
        repo.clear_cart(user_id)
        delete_selection[user_id] = set()
        bot.edit_message_text("Liste gelöscht! 🧹", user_id, msg_id, reply_markup=kb.main_menu(0))
        bot.answer_callback_query(call.id, "Die Liste wurde geleert")

    # --- DELETE MODE: select items to delete with confirmation ---
    elif call.data == "del_mode":
        delete_selection[user_id] = set()
        cart = repo.get_cart_items(user_id)
        bot.edit_message_reply_markup(
            user_id, msg_id,
            reply_markup=kb.final_cart_menu(
                cart,
                delete_mode=True,
                selected=delete_selection[user_id],
                confirm_delete=False
            )
        )
        bot.answer_callback_query(call.id, "Markieren Sie unnötige Waren")

    elif call.data.startswith("sel_del_"):
        p_id = int(call.data.split("_")[2])
        sel = delete_selection.setdefault(user_id, set())
        sel.remove(p_id) if p_id in sel else sel.add(p_id)

        cart = repo.get_cart_items(user_id)
        bot.edit_message_reply_markup(
            user_id, msg_id,
            reply_markup=kb.final_cart_menu(cart, delete_mode=True, selected=sel, confirm_delete=False)
        )

    elif call.data == "del_selected":
        sel = delete_selection.get(user_id, set())
        if not sel:
            bot.answer_callback_query(call.id, "Nichts zu löschen", show_alert=True)
            return

        cart = repo.get_cart_items(user_id)
        bot.edit_message_reply_markup(
            user_id, msg_id,
            reply_markup=kb.final_cart_menu(cart, delete_mode=True, selected=sel, confirm_delete=True)
        )

    elif call.data == "del_confirm_yes":
        sel = delete_selection.get(user_id, set())
        for p_id in sel:
            repo.mark_deleted(user_id, p_id)

        delete_selection[user_id] = set()
        cart = repo.get_cart_items(user_id)
        bot.edit_message_reply_markup(user_id, msg_id, reply_markup=kb.final_cart_menu(cart))
        bot.answer_callback_query(call.id)

    elif call.data == "del_confirm_no":
        sel = delete_selection.get(user_id, set())
        cart = repo.get_cart_items(user_id)
        bot.edit_message_reply_markup(
            user_id, msg_id,
            reply_markup=kb.final_cart_menu(cart, delete_mode=True, selected=sel, confirm_delete=False)
        )
        bot.answer_callback_query(call.id)

    elif call.data == "del_cancel":
        delete_selection[user_id] = set()
        cart = repo.get_cart_items(user_id)
        bot.edit_message_reply_markup(user_id, msg_id, reply_markup=kb.final_cart_menu(cart))
        bot.answer_callback_query(call.id)

    # 5) Toggle bought
    elif call.data.startswith('toggle_'):
        data = call.data.split('_')
        p_id = int(data[1])
        owner_id = int(data[2]) if len(data) > 2 else user_id

        repo.toggle_bought_status(owner_id, p_id)
        cart = repo.get_cart_items(owner_id)

        if call.inline_message_id:
            bot.edit_message_reply_markup(
                inline_message_id=call.inline_message_id,
                reply_markup=kb.shared_cart_menu(cart, owner_id)
            )
        else:
            bot.edit_message_reply_markup(user_id, msg_id, reply_markup=kb.final_cart_menu(cart))

    # 6) Legacy Delete (если где-то ещё есть del_{id})
    elif call.data.startswith('del_'):
        data = call.data.split('_')
        p_id = int(data[1])
        owner_id = int(data[2]) if len(data) > 2 else user_id

        repo.mark_deleted(owner_id, p_id)
        cart = repo.get_cart_items(owner_id)

        if call.inline_message_id:
            if not cart:
                bot.edit_message_text("Die Liste ist leer!", inline_message_id=call.inline_message_id)
            else:
                bot.edit_message_reply_markup(
                    inline_message_id=call.inline_message_id,
                    reply_markup=kb.shared_cart_menu(cart, owner_id)
                )
        else:
            if not cart:
                bot.edit_message_text("Die Liste ist leer!", user_id, msg_id, reply_markup=kb.main_menu(0))
            else:
                bot.edit_message_reply_markup(user_id, msg_id, reply_markup=kb.final_cart_menu(cart))

        bot.answer_callback_query(call.id)

    # 7) +/- edit qty (edit mode steps)
    elif call.data.startswith(('plus_', 'minus_')):
        parts = call.data.split('_')
        is_plus = (parts[0] == 'plus')
        p_id = int(parts[1])

        cart_service.change_item_qty(user_id, p_id, is_plus=is_plus, mode="edit")

        cart = repo.get_cart_items(user_id)
        bot.edit_message_reply_markup(
            user_id, msg_id,
            reply_markup=kb.final_cart_menu(cart, edit_mode=True)
        )

    # mode switch
    elif call.data == "mode_edit":
        cart = repo.get_cart_items(user_id)
        bot.edit_message_reply_markup(
            user_id, msg_id,
            reply_markup=kb.final_cart_menu(cart, edit_mode=True)
        )

    elif call.data == "mode_view":
        cart = repo.get_cart_items(user_id)
        bot.edit_message_reply_markup(
            user_id, msg_id,
            reply_markup=kb.final_cart_menu(cart, edit_mode=False)
        )

    # 8) Finish
    elif call.data.startswith('finish_shared_') or call.data in ["finish_list", "complete_shopping"]:
        if call.data.startswith('finish_shared_'):
            owner_id = int(call.data.split('_')[2])
        else:
            owner_id = user_id

        cart = repo.get_cart_items(owner_id)
        if not cart:
            bot.answer_callback_query(call.id, "Die Liste ist leer!", show_alert=True)
            return

        report = cart_service.build_finish_report(cart)
        repo.save_to_history_and_clear(owner_id)

        if call.inline_message_id:
            bot.edit_message_text(report, inline_message_id=call.inline_message_id, parse_mode="Markdown")
        else:
            try:
                bot.delete_message(user_id, msg_id)
            except Exception:
                pass

            bot.send_message(user_id, report, parse_mode="Markdown")
            bot.send_message(user_id, "🏁🏁🏁🏁🏁🏁🏁🏁🏁", reply_markup=kb.start_new_menu())

        bot.answer_callback_query(call.id)


@bot.inline_handler(func=lambda query: query.query == "share")
def query_text(inline_query):
    user_id = inline_query.from_user.id
    items = repo.get_cart_items(user_id)
    if not items:
        return

    text = f"🛒 *Einkaufsliste von {inline_query.from_user.first_name}:*"
    result = types.InlineQueryResultArticle(
        id='1',
        title="Einkaufsliste senden",
        input_message_content=types.InputTextMessageContent(text, parse_mode="Markdown"),
        reply_markup=kb.shared_cart_menu(items, user_id)
    )
    bot.answer_inline_query(inline_query.id, [result], cache_time=1)


def parse_qty_and_unit(raw: str):
    """
    Parses one item like:
      'грецкие орехи 300 грамм' -> ('грецкие орехи', 0.3, 'kg')
      'milk 2'                  -> ('milk', 2.0, None)
      '2 kg tomates'            -> ('tomates', 2.0, 'kg')

    Returns: (item_name, quantity_or_None, unit_hint_or_None)
    unit_hint: 'kg' | 'liter' | 'st' | None
    """
    s = raw.strip()

    # normalize (case + common unit spellings)
    t = s.lower()
    t = t.replace("килограмм", "kg").replace("килограмма", "kg").replace("кг", "kg")
    t = t.replace("граммов", "g").replace("грамм", "g").replace("гр", "g").replace("г", "g")
    t = t.replace("литров", "l").replace("литра", "l").replace("литр", "l").replace("л", "l")
    t = t.replace("liter", "l").replace("litre", "l")
    t = t.replace("stück", "st").replace("stk", "st").replace("шт", "st")

    def to_float(x: str) -> float:
        return float(x.replace(",", "."))

    item_name = s.strip()
    quantity = None
    unit = None

    # name + qty + unit (at END)
    m_end = re.search(r"^(.*?)\s+(\d+[.,]?\d*)\s*(kg|g|l|st)?$", t)
    # qty + unit + name (at START)
    m_start = re.search(r"^(\d+[.,]?\d*)\s*(kg|g|l|st)?\s*(.*)$", t)

    if m_end:
        item_name = m_end.group(1).strip()
        quantity = to_float(m_end.group(2))
        unit = m_end.group(3)
    elif m_start and m_start.group(3).strip():
        quantity = to_float(m_start.group(1))
        unit = m_start.group(2)
        item_name = m_start.group(3).strip()

    # convert grams -> kg
    if quantity is not None and unit == "g":
        quantity = round(quantity / 1000.0, 3)
        unit = "kg"

    # map to your DB unit_type values
    unit_hint = None
    if unit == "kg":
        unit_hint = "kg"
    elif unit == "l":
        unit_hint = "liter"
    elif unit == "st":
        unit_hint = "st"

    # keep original casing for display (optional)
    # we’ll use item_name as parsed from normalized string; it’s ok.
    return item_name, quantity, unit_hint

@bot.message_handler(func=lambda message: message.text and message.text.startswith('#'))
def handle_quick_add(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    global last_list_msg

    input_text = message.text[1:].strip()
    if not input_text:
        return

    raw_items = [i.strip() for i in input_text.replace('\n', ',').split(',') if i.strip()]

    for item_raw in raw_items:
        item_name, quantity, unit_hint = parse_qty_and_unit(item_raw)
        if not item_name:
            continue

        product_id = product_service.find_product_smart(item_name)

        if product_id:
            meta = repo.get_product_meta(product_id)
            unit_type_db, category_db = None, None

            if meta:
                unit_type_db, category_db, _ = meta

                # ✅ If it's a custom product and user specified unit -> update unit_type in DB for correct UI
                if category_db == "other" and unit_hint and unit_hint != unit_type_db:
                    repo.update_product_unit_type(product_id, unit_hint)
                    unit_type_db = unit_hint  # update locally too

            # ✅ If user didn't specify quantity -> use default step rules
            if quantity is None:
                if unit_type_db and category_db:
                    quantity = cart_service.calc_step(product_id, unit_type_db, category_db, mode="menu")
                else:
                    quantity = 1.0

            product_service.add_to_cart_smart(user_id, product_id, quantity)

        else:
            # New custom product
            if quantity is None:
                quantity = 1.0

            product_service.add_unknown_to_cart(
                user_id,
                item_name,
                quantity,
                unit_type=(unit_hint or "st")
            )

    # UI refresh: delete previous list message
    if user_id in last_list_msg:
        try:
            bot.delete_message(chat_id, last_list_msg[user_id])
        except Exception:
            pass

    cart = repo.get_cart_items(user_id)
    if not cart:
        return

    msg_text = "🛒 **Aktuelle Einkaufsliste:**\n\n"
    for item in cart:
        status = "✅" if item[4] == 1 else "▫️"
        display_qty = int(item[3]) if item[3] % 1 == 0 else item[3]
        unit = "kg" if item[5] == "kg" else "l" if item[5] == "liter" else "st"
        msg_text += f"{status} {item[2]} {item[1]} — {display_qty} {unit}\n"

    sent_msg = bot.send_message(
        chat_id,
        msg_text,
        parse_mode="Markdown",
        reply_markup=kb.final_cart_menu(cart)
    )
    last_list_msg[user_id] = sent_msg.message_id