import telebot
from telebot import types
from database import init_db, get_products_by_cat, get_cart_items, clear_cart, toggle_bought_status, \
    delete_from_cart, save_to_history, add_to_cart_smart, get_category_by_id
import keyboards as kb
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    init_db()
    # Adding cart count to main menu
    cart = get_cart_items(message.from_user.id)
    bot.send_message(message.chat.id, "Wählen Sie eine Kategorie:", reply_markup=kb.main_menu(len(cart)))

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    user_id = call.from_user.id
    msg_id = call.message.message_id if call.message else None

    # 1. Selecting a category
    if call.data.startswith('cat_'):
        category = call.data.replace('cat_', '')
        products = get_products_by_cat(category)
        cart = get_cart_items(user_id)  # Getting the full list
        # Pass 'cart' (list), NOT 'len(cart)'
        bot.edit_message_text("Wählen Sie Produkte aus:", user_id, msg_id,
                              reply_markup=kb.products_menu(products, cart))

    elif call.data == "back_to_main":
        # 1. Get the current cart items to show the correct count on the button
        cart = get_cart_items(user_id)
        # 2. Pass len(cart) to the main_menu function
        bot.edit_message_text("Hauptmenü:", user_id, msg_id,
                              reply_markup=kb.main_menu(len(cart)))

    # 2. Adding a product
    elif call.data.startswith('add_'):
        p_id = int(call.data.split('_')[1])
        add_to_cart_smart(user_id, p_id)
        category = get_category_by_id(p_id)
        products = get_products_by_cat(category)
        cart = get_cart_items(user_id)  # Getting the full list
        # Pass 'cart' (list)
        bot.edit_message_reply_markup(chat_id=user_id, message_id=msg_id,
                                      reply_markup=kb.products_menu(products, cart))
        bot.answer_callback_query(call.id, "Hinzugefügt!")

    # 3. Show list
    elif call.data == "show_cart":
        cart = get_cart_items(user_id)
        if not cart:
            bot.answer_callback_query(call.id, "Die Liste ist leer!", show_alert=True)
        else:
            bot.edit_message_text("Ihre Einkaufsliste:", user_id, msg_id, reply_markup=kb.final_cart_menu(cart))

    # 4. Clear / Back
    elif call.data == "clear_confirm":
        clear_cart(user_id)  # Calling the function we added to database.py
        # Fix: Arguments order (text, chat_id, message_id)
        bot.edit_message_text("Liste gelöscht! 🧹", user_id, msg_id, reply_markup=kb.main_menu(0))
        bot.answer_callback_query(call.id, "Die Liste wurde geleert")

    # 5. TOGGLE (purchased status)
    elif call.data.startswith('toggle_'):
        data = call.data.split('_')
        p_id = int(data[1])
        owner_id = int(data[2]) if len(data) > 2 else user_id

        toggle_bought_status(owner_id, p_id)
        cart = get_cart_items(owner_id)

        if call.inline_message_id:
            bot.edit_message_reply_markup(inline_message_id=call.inline_message_id,
                                          reply_markup=kb.shared_cart_menu(cart, owner_id))
        else:
            bot.edit_message_reply_markup(user_id, msg_id, reply_markup=kb.final_cart_menu(cart))

    # 6. DELETE
    elif call.data.startswith('del_'):
        data = call.data.split('_')
        p_id = int(data[1])
        owner_id = int(data[2]) if len(data) > 2 else user_id

        delete_from_cart(owner_id, p_id)
        cart = get_cart_items(owner_id)

        if call.inline_message_id:
            if not cart:
                bot.edit_message_text("Die Liste ist leer!", inline_message_id=call.inline_message_id)
            else:
                bot.edit_message_reply_markup(inline_message_id=call.inline_message_id,
                                              reply_markup=kb.shared_cart_menu(cart, owner_id))
        else:
            if not cart:
                bot.edit_message_text("Die Liste ist leer!", user_id, msg_id, reply_markup=kb.main_menu(0))
            else:
                bot.edit_message_reply_markup(user_id, msg_id, reply_markup=kb.final_cart_menu(cart))
        bot.answer_callback_query(call.id, "Gelöscht")

    # 7. FINISH
        # 7. FINISH (completion)
    elif call.data.startswith('finish_shared_') or call.data in ["finish_list", "complete_shopping"]:
        if call.data.startswith('finish_shared_'):
            owner_id = int(call.data.split('_')[2])
        else:
            owner_id = user_id

        # 1. Get items BEFORE they are deleted from DB
        cart = get_cart_items(owner_id)
        if not cart:
            bot.answer_callback_query(call.id, "Die Liste ist leer!", show_alert=True)
            return

        # 2. Generate the report text
            # Report generation
        bought_text, skipped_text = "", ""
        for item in cart:
            # item[4] — это статус is_bought
            status = item[4]
            u_name = "kg" if item[5] == "kg" else "l" if item[5] == "liter" else "st"
            display_qty = int(item[3]) if item[3] % 1 == 0 else item[3]
            line = f"• {item[2]} {item[1]} — {display_qty} {u_name}\n"

            if status == 1:
                    bought_text += line
            else:
                # Both regular (0) and marked as deleted (-1) will be included here.
                skipped_text += line

        report = "🏁 *Der Kauf ist abgeschlossen!*\n\n"
        if bought_text:
            report += "✅ *Gekauft:*\n" + bought_text + "\n"
        if skipped_text:
            report += "❌ *Nicht gekauft (gelöscht):*\n" + skipped_text

        # 3. ONLY NOW save to history and clear the cart table
        save_to_history(owner_id)

        # 4. Send the generated report
        if call.inline_message_id:
            bot.edit_message_text(report, inline_message_id=call.inline_message_id, parse_mode="Markdown")
        else:
            try:
                bot.delete_message(user_id, msg_id)
            except:
                pass

            # Sent report
            bot.send_message(user_id, report, parse_mode="Markdown")

            # Button for a new list
            bot.send_message(
                user_id,
                "$$$$$$$$$$$$$$",
                reply_markup=kb.start_new_menu()  # Используем готовую функцию
            )

        bot.answer_callback_query(call.id, "Fertig!")

@bot.inline_handler(func=lambda query: query.query == "share")
def query_text(inline_query):
    user_id = inline_query.from_user.id
    items = get_cart_items(user_id)
    if not items: return

    text = f"🛒 *Einkaufsliste von {inline_query.from_user.first_name}:*"
    result = types.InlineQueryResultArticle(
        id='1',
        title="Einkaufsliste senden",
        input_message_content=types.InputTextMessageContent(text, parse_mode="Markdown"),
        reply_markup=kb.shared_cart_menu(items, user_id)
    )
    bot.answer_inline_query(inline_query.id, [result], cache_time=1)

