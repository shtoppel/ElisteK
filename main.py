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
    bot.send_message(message.chat.id, "Wählen Sie eine Kategorie:", reply_markup=kb.main_menu())


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    user_id = call.from_user.id

    # To avoid writing if call.message everywhere, let's define the message ID once.
    # Inline call.message will be None, so we'll use a placeholder.
    msg_id = call.message.message_id if call.message else None

    # 1. Selecting a category
    if call.data.startswith('cat_'):
        category = call.data.split('_')[1]
        products = get_products_by_cat(category)
        cart = get_cart_items(user_id)
        bot.edit_message_text("Wählen Sie Produkte aus:", user_id, msg_id, reply_markup=kb.products_menu(products, cart))

    # 2. Adding a product
    elif call.data.startswith('add_'):
        p_id = int(call.data.split('_')[1])
        add_to_cart_smart(user_id, p_id)
        category = get_category_by_id(p_id)
        products = get_products_by_cat(category)
        cart = get_cart_items(user_id)
        bot.edit_message_reply_markup(chat_id=user_id, message_id=msg_id, reply_markup=kb.products_menu(products, cart))
        bot.answer_callback_query(call.id, "Hinzugefügt!")

    # 3. Show list
    elif call.data == "show_cart":
        cart = get_cart_items(user_id)
        if not cart:
            bot.answer_callback_query(call.id, "Die Liste ist leer!")
        else:
            bot.edit_message_text("Ihre Einkaufsliste:", user_id, msg_id, reply_markup=kb.final_cart_menu(cart))

    #4. Clear / Back
    elif call.data == "clear_confirm":
        clear_cart(user_id)
        bot.edit_message_text("Liste gelöscht!", user_id, msg_id, reply_markup=kb.main_menu())

    elif call.data == "back_to_main":
        bot.edit_message_text("Hauptmenü:", user_id, msg_id, reply_markup=kb.main_menu())

    #5. TOGGLE (purchased status) - SHARING SUPPORT
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

    #6. DELETE (deletion) - SHARING SUPPORT
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
                bot.edit_message_text("Die Liste ist leer!", user_id, msg_id, reply_markup=kb.main_menu())
            else:
                bot.edit_message_reply_markup(user_id, msg_id, reply_markup=kb.final_cart_menu(cart))
        bot.answer_callback_query(call.id, "Gelöscht")

    #7. FINISH (completion) - UNIFIED LOGIC
    elif call.data.startswith('finish_shared_') or call.data in ["finish_list", "complete_shopping"]:
        if call.data.startswith('finish_shared_'):
            owner_id = int(call.data.split('_')[2])
        else:
            owner_id = user_id

        cart = get_cart_items(owner_id)
        if not cart:
            bot.answer_callback_query(call.id, "Die Liste ist leer!", show_alert=True)
            return

        # Report generation
        bought_text, skipped_text = "", ""
        for item in cart:
            u_name = "кг" if item[5] == "kg" else "л" if item[5] == "liter" else "шт"
            display_qty = int(item[3]) if item[3] % 1 == 0 else item[3]
            line = f"• {item[2]} {item[1]} — {display_qty} {u_name}\n"
            if item[4] == 1:
                bought_text += line
            else:
                skipped_text += line

        report = "🏁 *Der Kauf ist abgeschlossen!*\n\n"
        if bought_text: report += "✅ *Gekauft:*\n" + bought_text + "\n"
        if skipped_text: report += "❌ *Nicht gekauft (gelöscht):*\n" + skipped_text

        save_to_history(owner_id)  # We clean up the database

        if call.inline_message_id:
            # If the partner has finished online
            bot.edit_message_text(report, inline_message_id=call.inline_message_id, parse_mode="Markdown")
        else:
            # If the owner himself finished in the chat
            try:
                bot.delete_message(user_id, msg_id)
            except:
                pass
            bot.send_message(user_id, report, parse_mode="Markdown")
            bot.send_message(user_id, "Liste gelöscht.", reply_markup=kb.start_new_menu())

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


if __name__ == '__main__':
    bot.polling(none_stop=True)