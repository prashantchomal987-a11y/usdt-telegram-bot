import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "8034636115:AAGwn2gUSuYBzkfjmb-IbcHZRmtXhTQPw3o"
ADMIN_ID = 1603929921  # apni telegram id

bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}

# ---------- START ----------
@bot.message_handler(commands=['start'])
def start(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("💰 Buy USDT", callback_data="buy"),
        InlineKeyboardButton("💸 Sell USDT", callback_data="sell")
    )
    bot.send_message(
        message.chat.id,
        "Welcome to USDT Buy & Sell Bot\n\nChoose an option 👇",
        reply_markup=keyboard
    )

# ---------- BUTTON CLICK ----------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "buy":
        user_data[call.from_user.id] = {"type": "BUY"}
        bot.send_message(call.message.chat.id, "Enter USDT amount to BUY:")
    elif call.data == "sell":
        user_data[call.from_user.id] = {"type": "SELL"}
        bot.send_message(call.message.chat.id, "Enter USDT amount to SELL:")
    elif call.data.startswith("approve"):
        uid = int(call.data.split("_")[1])
        bot.send_message(uid, "✅ Your order has been APPROVED")
        bot.answer_callback_query(call.id, "Order Approved")
    elif call.data.startswith("reject"):
        uid = int(call.data.split("_")[1])
        bot.send_message(uid, "❌ Your order has been REJECTED")
        bot.answer_callback_query(call.id, "Order Rejected")

# ---------- TEXT HANDLER ----------
@bot.message_handler(func=lambda m: True, content_types=['text'])
def text_handler(message):
    uid = message.from_user.id

    if uid in user_data and "amount" not in user_data[uid]:
        user_data[uid]["amount"] = message.text
        bot.send_message(
            message.chat.id,
            "Payment Method:\n\n"
            "✅ BharatPe UPI\n"
            "✅ Bank Transfer\n\n"
            "Payment karne ke baad screenshot bhejo 📸"
        )
    else:
        bot.send_message(message.chat.id, "Please use /start")

# ---------- PHOTO (PAYMENT PROOF) ----------
@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    uid = message.from_user.id

    if uid not in user_data:
        bot.send_message(message.chat.id, "Please use /start first")
        return

    data = user_data[uid]

    caption = (
        f"🆕 New USDT Order\n\n"
        f"👤 User ID: {uid}\n"
        f"🔁 Type: {data['type']}\n"
        f"💰 Amount: {data['amount']} USDT"
    )

    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("✅ Approve", callback_data=f"approve_{uid}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"reject_{uid}")
    )

    bot.send_photo(
        ADMIN_ID,
        message.photo[-1].file_id,
        caption=caption,
        reply_markup=keyboard
    )

    bot.send_message(
        message.chat.id,
        "⏳ Payment received.\nAdmin verification in process."
    )

    user_data.pop(uid)

# ---------- RUN ----------
bot.polling()

