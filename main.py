import telebot
from database import init_db, get_products_by_cat, get_cart_items, clear_cart, toggle_bought_status, \
    delete_from_cart, save_to_history, add_to_cart_smart, get_category_by_id
import keyboards as kb
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')

bot = telebot.TeleBot(TOKEN)

# Temporary storage of selected products
user_carts = {}

@bot.message_handler(commands=['start'])
def start(message):
    init_db()
    bot.send_message(message.chat.id, "Выберите категорию:", reply_markup=kb.main_menu())


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    user_id = call.from_user.id

    # 1. Category selection
    if call.data.startswith('cat_'):
        category = call.data.split('_')[1]
        products = get_products_by_cat(category)
        cart = get_cart_items(user_id)
        bot.edit_message_text("Выберите товары (нажмите повторно для +1):",
                              user_id, call.message.message_id,
                              reply_markup=kb.products_menu(products, cart))

    # 2. Adding a product
    elif call.data.startswith('add_'):
        p_id = int(call.data.split('_')[1])

        # 1. Add a product (the smart function will automatically determine the step of 0.5 or 10)
        add_to_cart_smart(user_id, p_id)

        #2: Find out the category to update the menu
        category = get_category_by_id(p_id)

        #3. Receive updated data
        products = get_products_by_cat(category)
        cart = get_cart_items(user_id)

        #4. Update the buttons (the checkmark will appear immediately)
        bot.edit_message_reply_markup(
            chat_id=user_id,
            message_id=call.message.message_id,
            reply_markup=kb.products_menu(products, cart)
        )
        bot.answer_callback_query(call.id, "Добавлено!")

    # 3. Show list
    elif call.data == "show_cart":
        cart = get_cart_items(user_id)
        if not cart:
            bot.answer_callback_query(call.id, "Список пуст!")
        else:
            bot.edit_message_text("Ваш список покупок:", user_id,
                                  call.message.message_id,
                                  reply_markup=kb.final_cart_menu(cart))

    # 4. Clear list
    elif call.data == "clear_confirm":
        clear_cart(user_id)
        bot.edit_message_text("Список очищен!", user_id,
                              call.message.message_id,
                              reply_markup=kb.main_menu())

    elif call.data == "back_to_main":
        bot.edit_message_text("Главное меню:", user_id,
                              call.message.message_id,
                              reply_markup=kb.main_menu())

    # Logic for switching the "Purchased" status
    elif call.data.startswith('toggle_'):
        p_id = int(call.data.split('_')[1])
        toggle_bought_status(user_id, p_id)

    # Redraw the list to see the changes (crossing out)
        cart = get_cart_items(user_id)
        bot.edit_message_reply_markup(
            chat_id=user_id,
            message_id=call.message.message_id,
            reply_markup=kb.final_cart_menu(cart)
        )

    # Logic for deleting a product from the list
    elif call.data.startswith('del_'):
        p_id = int(call.data.split('_')[1])
        delete_from_cart(user_id, p_id)

        cart = get_cart_items(user_id)
        if not cart:
            bot.edit_message_text("Список пуст!", user_id, call.message.message_id, reply_markup=kb.main_menu())
        else:
            bot.edit_message_reply_markup(
                chat_id=user_id,
                message_id=call.message.message_id,
                reply_markup=kb.final_cart_menu(cart)
            )
        bot.answer_callback_query(call.id, "Удалено")





    elif call.data in ["finish_list", "complete_shopping"]:

        cart = get_cart_items(user_id)

        if not cart:
            bot.answer_callback_query(call.id, "Список пуст!", show_alert=True)
            return

        bought_text = ""
        skipped_text = ""

        for item in cart:

            # We securely retrieve data, no matter how much there is

            p_id = item[0]

            name = item[1]

            emoji = item[2]

            qty = item[3]

            status = item[4]

            unit = item[5]

            u_name = "кг" if unit == "kg" else "л" if unit == "liter" else "шт"

            display_qty = int(qty) if qty % 1 == 0 else qty

            line = f"• {emoji} {name} — {display_qty} {u_name}\n"

            if status == 1:

                bought_text += line

            else:

                skipped_text += line

        # Here we are generating a final report

        report = "🏁 *Покупка завершена!*\n\n"

        if bought_text:
            report += "✅ *Куплено:*\n" + bought_text + "\n"

        if skipped_text:
            report += "❌ *Не куплено (удалено):*\n" + skipped_text

        # Save the PURCHASED items in history and delete EVERYTHING from the cart

        save_to_history(user_id)

        #1. Delete the old message with buttons (to avoid confusing the user)

        try:

            bot.delete_message(user_id, call.message.message_id)

        except:

            pass

        # 2. Send the report

        bot.send_message(user_id, report, parse_mode="Markdown")

        #3. Send a new button for a new start

        bot.send_message(

            user_id,

            "Список очищен. Нажми кнопку ниже, когда захочешь составить новый.",

            reply_markup=kb.start_new_menu()

        )

        bot.answer_callback_query(call.id, "Готово!")